#include "lsd_engine.hpp"
#include <cmath>
#include <random>
#include <algorithm>
#include <unordered_map>
#include <iostream>
#include <chrono>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace lsdembed {

// Spatial hash grid for O(N) force calculations
class SpatialHashGrid {
private:
    double cell_size_;
    std::unordered_map<uint64_t, std::vector<int>> grid_;
    
    uint64_t hash_position(const std::vector<double>& pos) {
        int x = static_cast<int>(std::floor(pos[0] / cell_size_));
        int y = static_cast<int>(std::floor(pos[1] / cell_size_));
        int z = (pos.size() > 2) ? static_cast<int>(std::floor(pos[2] / cell_size_)) : 0;
        
        // Simple hash function for 3D coordinates
        return static_cast<uint64_t>(x) * 73856093ULL ^ 
               static_cast<uint64_t>(y) * 19349663ULL ^ 
               static_cast<uint64_t>(z) * 83492791ULL;
    }

public:
    SpatialHashGrid(double cell_size) : cell_size_(cell_size) {}
    
    void clear() {
        grid_.clear();
    }
    
    void add_particle(int particle_id, const std::vector<double>& position) {
        uint64_t hash = hash_position(position);
        grid_[hash].push_back(particle_id);
    }
    
    std::vector<int> get_neighbors(int particle_id, const std::vector<double>& position, double radius) {
        std::vector<int> neighbors;
        int grid_radius = static_cast<int>(std::ceil(radius / cell_size_));
        
        int base_x = static_cast<int>(std::floor(position[0] / cell_size_));
        int base_y = static_cast<int>(std::floor(position[1] / cell_size_));
        int base_z = (position.size() > 2) ? static_cast<int>(std::floor(position[2] / cell_size_)) : 0;
        
        for (int dx = -grid_radius; dx <= grid_radius; ++dx) {
            for (int dy = -grid_radius; dy <= grid_radius; ++dy) {
                for (int dz = (position.size() > 2 ? -grid_radius : 0); 
                     dz <= (position.size() > 2 ? grid_radius : 0); ++dz) {
                    
                    std::vector<double> cell_pos = {
                        static_cast<double>(base_x + dx) * cell_size_,
                        static_cast<double>(base_y + dy) * cell_size_
                    };
                    if (position.size() > 2) {
                        cell_pos.push_back(static_cast<double>(base_z + dz) * cell_size_);
                    }
                    
                    uint64_t hash = hash_position(cell_pos);
                    auto it = grid_.find(hash);
                    if (it != grid_.end()) {
                        for (int neighbor_id : it->second) {
                            if (neighbor_id != particle_id) {
                                neighbors.push_back(neighbor_id);
                            }
                        }
                    }
                }
            }
        }
        return neighbors;
    }
};

LSDEngine::LSDEngine(const LSDParams& params) : params_(params) {
    std::cout << "Initializing LSD Engine with d=" << params_.d 
              << ", alpha=" << params_.alpha << ", beta=" << params_.beta << std::endl;
}

void LSDEngine::set_params(const LSDParams& params) {
    params_ = params;
}

LSDParams LSDEngine::get_params() const {
    return params_;
}

void LSDEngine::compute_forces(
    const std::vector<std::vector<double>>& positions,
    std::vector<std::vector<double>>& forces,
    double alpha, double beta, double r_cutoff
) {
    const int N = positions.size();
    const int d = positions[0].size();
    const double r_cutoff_sq = r_cutoff * r_cutoff;
    const double epsilon = 1e-6;
    
    // Clear forces
    for (auto& force : forces) {
        std::fill(force.begin(), force.end(), 0.0);
    }
    
    // Use spatial hashing for better performance
    SpatialHashGrid grid(r_cutoff);
    
    // Add all particles to grid
    for (int i = 0; i < N; ++i) {
        grid.add_particle(i, positions[i]);
    }
    
    // Universal Repulsion with spatial optimization
    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < N; ++i) {
        std::vector<int> neighbors = grid.get_neighbors(i, positions[i], r_cutoff);
        
        for (int j : neighbors) {
            if (j <= i) continue; // Avoid double computation
            
            double dist_sq = 0.0;
            std::vector<double> diff(d);
            
            // Calculate distance and difference vector
            for (int k = 0; k < d; ++k) {
                diff[k] = positions[i][k] - positions[j][k];
                dist_sq += diff[k] * diff[k];
            }
            
            if (dist_sq < r_cutoff_sq && dist_sq > epsilon) {
                double dist = std::sqrt(dist_sq);
                double force_magnitude = alpha / (dist_sq + epsilon);
                
                // Apply forces (Newton's third law)
                for (int k = 0; k < d; ++k) {
                    double force_component = force_magnitude * diff[k] / dist;
                    
                    #pragma omp atomic
                    forces[i][k] += force_component;
                    
                    #pragma omp atomic
                    forces[j][k] -= force_component;
                }
            }
        }
    }
    
    // Sequential Spring Attraction
    for (int i = 0; i < N - 1; ++i) {
        for (int k = 0; k < d; ++k) {
            double diff = positions[i+1][k] - positions[i][k];
            double force_component = beta * diff;
            
            forces[i][k] += force_component;
            forces[i+1][k] -= force_component;
        }
    }
}

void LSDEngine::integrate_motion_damped(
    std::vector<std::vector<double>>& positions,
    std::vector<std::vector<double>>& velocities,
    const std::vector<double>& masses,
    int steps
) {
    const int N = positions.size();
    const int d = positions[0].size();
    const double dt = params_.dt;
    const double gamma = params_.gamma;
    
    std::vector<std::vector<double>> forces(N, std::vector<double>(d, 0.0));
    std::vector<std::vector<double>> acceleration(N, std::vector<double>(d, 0.0));
    
    for (int step = 0; step < steps; ++step) {
        // Compute semantic forces
        compute_forces(positions, forces, params_.alpha, params_.beta, params_.r_cutoff);
        
        // Calculate acceleration: a = (F_semantic - gamma * v) / m
        #pragma omp parallel for
        for (int i = 0; i < N; ++i) {
            for (int k = 0; k < d; ++k) {
                double damping_force = -gamma * velocities[i][k];
                acceleration[i][k] = (forces[i][k] + damping_force) / masses[i];
            }
        }
        
        // Update positions: q += v*dt + 0.5*a*dt^2
        #pragma omp parallel for
        for (int i = 0; i < N; ++i) {
            for (int k = 0; k < d; ++k) {
                positions[i][k] += velocities[i][k] * dt + 0.5 * acceleration[i][k] * dt * dt;
            }
        }
        
        // Compute new forces for velocity update
        compute_forces(positions, forces, params_.alpha, params_.beta, params_.r_cutoff);
        
        // Update velocities using mid-point method
        #pragma omp parallel for
        for (int i = 0; i < N; ++i) {
            for (int k = 0; k < d; ++k) {
                double new_damping_force = -gamma * velocities[i][k];
                double new_acceleration = (forces[i][k] + new_damping_force) / masses[i];
                velocities[i][k] += 0.5 * (acceleration[i][k] + new_acceleration) * dt;
            }
        }
    }
}

std::vector<double> LSDEngine::embed_tokens(
    const std::vector<std::string>& tokens,
    const std::unordered_map<std::string, double>& idf_scores
) {
    const int N = tokens.size();
    const int d = params_.d;
    
    if (N == 0) {
        return std::vector<double>(d, 0.0);
    }
    
    // Initialize random positions and zero velocities
    std::mt19937 rng(params_.seed);
    std::normal_distribution<double> normal_dist(0.0, params_.scale);
    
    std::vector<std::vector<double>> positions(N, std::vector<double>(d));
    std::vector<std::vector<double>> velocities(N, std::vector<double>(d, 0.0));
    
    // Initialize positions
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < d; ++j) {
            positions[i][j] = normal_dist(rng);
        }
    }
    
    // Calculate masses from IDF scores
    std::vector<double> masses(N);
    double max_idf = 1.0;
    
    // Find maximum IDF for normalization
    for (const auto& pair : idf_scores) {
        max_idf = std::max(max_idf, pair.second);
    }
    
    for (int i = 0; i < N; ++i) {
        auto it = idf_scores.find(tokens[i]);
        double idf = (it != idf_scores.end()) ? it->second : 0.01;
        masses[i] = 1.0 / (idf + 0.01); // Inverse relationship: rare words = higher mass
    }
    
    // Run physics simulation
    integrate_motion_damped(positions, velocities, masses, N);
    
    // Calculate weighted centroid
    std::vector<double> result(d, 0.0);
    double total_weight = 0.0;
    
    for (int i = 0; i < N; ++i) {
        double weight = 1.0 / masses[i]; // Importance weight
        total_weight += weight;
        
        for (int j = 0; j < d; ++j) {
            result[j] += positions[i][j] * weight;
        }
    }
    
    // Normalize by total weight
    if (total_weight > 0.0) {
        for (int j = 0; j < d; ++j) {
            result[j] /= total_weight;
        }
    }
    
    return result;
}

std::vector<std::vector<double>> LSDEngine::embed_chunks(
    const std::vector<std::vector<std::string>>& token_chunks,
    const std::unordered_map<std::string, double>& idf_scores
) {
    const int num_chunks = token_chunks.size();
    std::vector<std::vector<double>> embeddings(num_chunks);
    
    std::cout << "Embedding " << num_chunks << " chunks..." << std::endl;
    
    // Memory-aware thread management
    #ifdef _OPENMP
    int max_threads = omp_get_max_threads();
    // Estimate memory usage per chunk (rough approximation)
    size_t estimated_memory_per_chunk = params_.d * sizeof(double) * 100; // Conservative estimate
    size_t total_estimated_memory = num_chunks * estimated_memory_per_chunk;
    
    // Adjust thread count based on memory considerations
    int optimal_threads = max_threads;
    if (total_estimated_memory > 1024 * 1024 * 1024) { // > 1GB
        optimal_threads = std::min(max_threads, static_cast<int>(num_chunks / 50));
    } else {
        optimal_threads = std::min(max_threads, static_cast<int>(num_chunks / 10));
    }
    optimal_threads = std::max(1, optimal_threads);
    
    std::cout << "Using " << optimal_threads << " threads (max available: " << max_threads << ")" << std::endl;
    omp_set_num_threads(optimal_threads);
    #endif
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Process chunks in parallel with memory monitoring
    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < num_chunks; ++i) {
        embeddings[i] = embed_tokens(token_chunks[i], idf_scores);
        
        // Progress reporting (thread-safe)
        if (i % 10 == 0) {
            #pragma omp critical
            {
                std::cout << "Processed " << i + 1 << "/" << num_chunks << " chunks\r" << std::flush;
            }
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    std::cout << "\nCompleted embedding in " << duration.count() << "ms" << std::endl;
    std::cout << "Average: " << (duration.count() / static_cast<double>(num_chunks)) 
              << "ms per chunk" << std::endl;
    
    return embeddings;
}

} // namespace lsdembed