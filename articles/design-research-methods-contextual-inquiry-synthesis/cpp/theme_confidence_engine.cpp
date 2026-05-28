#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct EvidenceUnit {
    int unit_id;
    std::string participant_group;
    std::string method;
    std::string primary_theme;
    double evidence_strength;
    double interpretive_risk;
};

struct ThemeAggregate {
    std::string theme;
    int evidence_units = 0;
    std::set<std::string> stakeholder_groups;
    std::set<std::string> methods;
    double total_strength = 0.0;
    double total_risk = 0.0;
    double confidence = 0.0;
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

std::vector<EvidenceUnit> read_evidence(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<EvidenceUnit> evidence;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 7) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        evidence.push_back(
            EvidenceUnit{
                std::stoi(fields[0]),
                fields[1],
                fields[2],
                fields[3],
                std::stod(fields[5]),
                std::stod(fields[6])
            }
        );
    }

    return evidence;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/contextual_inquiry_evidence_units_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto evidence = read_evidence(input_path);
        std::map<std::string, ThemeAggregate> aggregates;

        for (const auto& unit : evidence) {
            auto& agg = aggregates[unit.primary_theme];
            agg.theme = unit.primary_theme;
            agg.evidence_units += 1;
            agg.stakeholder_groups.insert(unit.participant_group);
            agg.methods.insert(unit.method);
            agg.total_strength += unit.evidence_strength;
            agg.total_risk += unit.interpretive_risk;
        }

        std::vector<ThemeAggregate> rows;
        for (auto& pair : aggregates) {
            auto& agg = pair.second;
            const double mean_strength = agg.total_strength / agg.evidence_units;
            const double mean_risk = agg.total_risk / agg.evidence_units;
            agg.confidence =
                0.35 * mean_strength +
                0.25 * static_cast<double>(agg.stakeholder_groups.size()) +
                0.25 * static_cast<double>(agg.methods.size()) -
                0.15 * mean_risk;
            rows.push_back(agg);
        }

        std::sort(
            rows.begin(),
            rows.end(),
            [](const ThemeAggregate& a, const ThemeAggregate& b) {
                return a.confidence > b.confidence;
            }
        );

        std::cout << "rank,theme,evidence_units,stakeholder_groups,methods,synthesis_confidence\n";
        for (std::size_t i = 0; i < rows.size(); ++i) {
            std::cout << (i + 1) << ","
                      << rows[i].theme << ","
                      << rows[i].evidence_units << ","
                      << rows[i].stakeholder_groups.size() << ","
                      << rows[i].methods.size() << ","
                      << std::fixed << std::setprecision(6)
                      << rows[i].confidence << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
