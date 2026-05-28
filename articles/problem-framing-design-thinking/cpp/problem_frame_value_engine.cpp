#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct ProblemFrame {
    std::string name;
    double explanatory_adequacy;
    double stakeholder_coverage;
    double opportunity_value;
    double framing_risk;
};

struct ScoredFrame {
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

std::vector<ProblemFrame> read_frames(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<ProblemFrame> frames;
    std::string line;

    std::getline(file, line); // header

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 5) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        frames.push_back(
            ProblemFrame{
                fields[0],
                to_double(fields[1]),
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4])
            }
        );
    }

    return frames;
}

double frame_value(const ProblemFrame& frame) {
    constexpr double we = 0.30;
    constexpr double ws = 0.25;
    constexpr double wo = 0.30;
    constexpr double wr = 0.15;

    return we * frame.explanatory_adequacy
         + ws * frame.stakeholder_coverage
         + wo * frame.opportunity_value
         - wr * frame.framing_risk;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/problem_frames_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto frames = read_frames(input_path);
        std::vector<ScoredFrame> scored;

        for (const auto& frame : frames) {
            scored.push_back(ScoredFrame{frame.name, frame_value(frame)});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredFrame& a, const ScoredFrame& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,frame,frame_value\n";
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
