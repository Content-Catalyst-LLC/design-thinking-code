#include <iostream>

// Toy design pathway value score.
// Educational only.
// Compile with: g++ cpp/design_value.cpp -o outputs/design_value

int main() {
    double human_relevance = 8.8;
    double feasibility = 7.4;
    double learning_value = 8.1;
    double residual_risk = 4.0;

    double value =
        0.35 * human_relevance +
        0.25 * feasibility +
        0.25 * learning_value -
        0.15 * residual_risk;

    std::cout << "Design value: " << value << "\n";
    return 0;
}
