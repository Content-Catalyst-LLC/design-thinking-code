#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Insight {
    std::string name;
    double pattern_support;
    double explanatory_depth;
    double opportunity_value;
    double interpretive_risk;
};

struct ScoredInsight {
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

std::vector<Insight> read_insights(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Insight> insights;
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

        insights.push_back(
            Insight{
                fields[0],
                to_double(fields[1]),
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4])
            }
        );
    }

    return insights;
}

double insight_value(const Insight& insight) {
    constexpr double wp = 0.30;
    constexpr double we = 0.30;
    constexpr double wo = 0.25;
    constexpr double wr = 0.15;

    return wp * insight.pattern_support
         + we * insight.explanatory_depth
         + wo * insight.opportunity_value
         - wr * insight.interpretive_risk;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/candidate_insights_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto insights = read_insights(input_path);
        std::vector<ScoredInsight> scored;

        for (const auto& insight : insights) {
            scored.push_back(ScoredInsight{insight.name, insight_value(insight)});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredInsight& a, const ScoredInsight& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,insight,insight_value\n";
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
