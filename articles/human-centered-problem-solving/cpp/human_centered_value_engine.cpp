#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct DesignOption {
    std::string name;
    double human_benefit;
    double usability;
    double stakeholder_fit;
    double burden;
};

struct ScoredOption {
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

std::vector<DesignOption> read_options(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<DesignOption> options;
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

        options.push_back(
            DesignOption{
                fields[0],
                to_double(fields[1]),
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4])
            }
        );
    }

    return options;
}

double human_centered_value(const DesignOption& option) {
    constexpr double wb = 0.30;
    constexpr double wu = 0.25;
    constexpr double ws = 0.30;
    constexpr double wc = 0.15;

    return wb * option.human_benefit
         + wu * option.usability
         + ws * option.stakeholder_fit
         - wc * option.burden;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/human_centered_options_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto options = read_options(input_path);
        std::vector<ScoredOption> scored;

        for (const auto& option : options) {
            scored.push_back(ScoredOption{option.name, human_centered_value(option)});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredOption& a, const ScoredOption& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,option,hc_value\n";
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
