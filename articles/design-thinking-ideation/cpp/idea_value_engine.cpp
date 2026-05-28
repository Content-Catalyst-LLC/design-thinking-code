#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Idea {
    std::string name;
    double desirability;
    double feasibility;
    double novelty;
    double equity_value;
    double learning_value;
    double residual_risk;
};

struct ScoredIdea {
    std::string name;
    double value;
};

double to_double(const std::string& value) {
    try {
        return std::stod(value);
    } catch (...) {
        throw std::runtime_error("Unable to parse numeric value: " + value);
    }
}

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream ss(line);
    std::string item;

    while (std::getline(ss, item, ',')) {
        fields.push_back(item);
    }

    return fields;
}

std::vector<Idea> read_ideas(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Idea> ideas;
    std::string line;

    std::getline(file, line); // header

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 8) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        ideas.push_back(
            Idea{
                fields[0],
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7])
            }
        );
    }

    return ideas;
}

double idea_value(const Idea& idea) {
    constexpr double wd = 0.24;
    constexpr double wf = 0.18;
    constexpr double wn = 0.18;
    constexpr double we = 0.18;
    constexpr double wl = 0.12;
    constexpr double wr = 0.10;

    return wd * idea.desirability
         + wf * idea.feasibility
         + wn * idea.novelty
         + we * idea.equity_value
         + wl * idea.learning_value
         - wr * idea.residual_risk;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/idea_portfolio_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto ideas = read_ideas(input_path);
        std::vector<ScoredIdea> scored;

        for (const auto& idea : ideas) {
            scored.push_back(ScoredIdea{idea.name, idea_value(idea)});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredIdea& a, const ScoredIdea& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,idea,idea_value\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].value << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
