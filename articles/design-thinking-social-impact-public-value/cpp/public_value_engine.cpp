#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Intervention {
    std::string name;
    double access;
    double equity;
    double dignity;
    double legitimacy;
    double accountability;
    double outcome_strength;
    double sustainability;
    double learning;
    double feasibility;
    double governance;
    double implementation_risk;
    double burden_risk;
    double participation;
    double community_value;
    double repair;
    double stewardship;
};

struct Scored {
    std::string name;
    double public_value;
    double readiness;
    double stewardship_need;
    double portfolio_priority;
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

double public_value(const Intervention& x) {
    return 0.13*x.access + 0.15*x.equity + 0.12*x.dignity +
           0.12*x.legitimacy + 0.13*x.accountability + 0.11*x.outcome_strength +
           0.08*x.sustainability + 0.07*x.learning + 0.05*x.community_value +
           0.04*x.repair;
}

double impact_readiness(const Intervention& x) {
    const double pv = public_value(x);
    return 0.30*pv + 0.17*x.feasibility + 0.16*x.governance +
           0.12*x.learning + 0.10*x.participation + 0.08*x.stewardship +
           0.07*x.repair - 0.07*x.implementation_risk - 0.07*x.burden_risk;
}

double stewardship_need(const Intervention& x) {
    return 0.24*x.implementation_risk + 0.22*x.burden_risk +
           0.16*(10.0-x.governance) + 0.12*(10.0-x.sustainability) +
           0.10*(10.0-x.learning) + 0.08*(10.0-x.repair) +
           0.08*(10.0-x.stewardship);
}

double portfolio_priority(const Intervention& x) {
    return 0.36*public_value(x) + 0.28*impact_readiness(x) +
           0.14*x.equity + 0.10*x.community_value + 0.06*x.participation -
           0.14*stewardship_need(x) - 0.06*x.implementation_risk;
}

std::vector<Intervention> read_interventions(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Intervention> interventions;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 18) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        interventions.push_back(
            Intervention{
                fields[0],
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7]),
                to_double(fields[8]),
                to_double(fields[9]),
                to_double(fields[10]),
                to_double(fields[11]),
                to_double(fields[12]),
                to_double(fields[13]),
                to_double(fields[14]),
                to_double(fields[15]),
                to_double(fields[16]),
                to_double(fields[17])
            }
        );
    }

    return interventions;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/social_impact_interventions_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto interventions = read_interventions(input_path);
        std::vector<Scored> scored;

        for (const auto& intervention : interventions) {
            scored.push_back(
                Scored{
                    intervention.name,
                    public_value(intervention),
                    impact_readiness(intervention),
                    stewardship_need(intervention),
                    portfolio_priority(intervention)
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const Scored& a, const Scored& b) {
                return a.portfolio_priority > b.portfolio_priority;
            }
        );

        std::cout << "rank,intervention,public_value_score,impact_readiness,stewardship_need,portfolio_priority\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].public_value << ","
                      << scored[i].readiness << ","
                      << scored[i].stewardship_need << ","
                      << scored[i].portfolio_priority << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
