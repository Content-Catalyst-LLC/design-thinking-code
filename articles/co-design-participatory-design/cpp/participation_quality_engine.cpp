#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct CodesignActivity {
    std::string name;
    double representation;
    double accessibility;
    double participant_influence;
    double trust_quality;
    double evidence_quality;
    double implementation_accountability;
    double decision_impact;
    double ethical_risk;
};

struct ScoredActivity {
    std::string name;
    double quality;
    double ethical_risk;
};

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream ss(line);
    std::string item;
    while (std::getline(ss, item, ',')) {
        fields.push_back(item);
    }
    return fields;
}

double to_double(const std::string& value) {
    try {
        return std::stod(value);
    } catch (...) {
        throw std::runtime_error("Unable to parse numeric value: " + value);
    }
}

double participation_quality(const CodesignActivity& x) {
    return 0.18 * x.representation +
           0.14 * x.accessibility +
           0.22 * x.participant_influence +
           0.12 * x.trust_quality +
           0.12 * x.evidence_quality +
           0.12 * x.implementation_accountability +
           0.14 * x.decision_impact -
           0.08 * x.ethical_risk;
}

std::vector<CodesignActivity> read_activities(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<CodesignActivity> activities;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 11) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        activities.push_back(
            CodesignActivity{
                fields[0],
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7]),
                to_double(fields[8]),
                to_double(fields[9]),
                to_double(fields[10])
            }
        );
    }

    return activities;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/codesign_activities_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto activities = read_activities(input_path);
        std::vector<ScoredActivity> scored;

        for (const auto& activity : activities) {
            scored.push_back(
                ScoredActivity{
                    activity.name,
                    participation_quality(activity),
                    activity.ethical_risk
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredActivity& a, const ScoredActivity& b) {
                return a.quality > b.quality;
            }
        );

        std::cout << "rank,activity,participation_quality,ethical_risk\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].quality << ","
                      << scored[i].ethical_risk << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
