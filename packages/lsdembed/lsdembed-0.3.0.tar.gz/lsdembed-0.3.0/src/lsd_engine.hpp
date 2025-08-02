#pragma once
#include <vector>
#include <unordered_map>
#include <string>
#include <memory>

namespace lsdembed {

struct LSDParams {
    int d = 512;
    double dt = 0.05;
    double alpha = 1.0;
    double beta = 0.5;
    double gamma = 0.2;
    double r_cutoff = 3.0;
    double scale = 0.1;
    int seed = 0;
};

class LSDEngine {
public:
    LSDEngine(const LSDParams& params = LSDParams{});
    
    // Core embedding functions
    std::vector<double> embed_tokens(
        const std::vector<std::string>& tokens,
        const std::unordered_map<std::string, double>& idf_scores
    );
    
    std::vector<std::vector<double>> embed_chunks(
        const std::vector<std::vector<std::string>>& token_chunks,
        const std::unordered_map<std::string, double>& idf_scores
    );
    
    // Utility functions
    void set_params(const LSDParams& params);
    LSDParams get_params() const;
    
private:
    LSDParams params_;
    
    // Core physics simulation
    void compute_forces(
        const std::vector<std::vector<double>>& positions,
        std::vector<std::vector<double>>& forces,
        double alpha, double beta, double r_cutoff
    );
    
    void integrate_motion_damped(
        std::vector<std::vector<double>>& positions,
        std::vector<std::vector<double>>& velocities,
        const std::vector<double>& masses,
        int steps
    );
};

} // namespace lsdembed