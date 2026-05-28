#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Option {
    std::string name;
    double desirability;
    double authority;
    double capability;
    double funding;
    double policy_fit;
    double governance;
    double trust_gain;
    double burden_reduction;
    double coordination;
    double implementation_risk;
    double data_readiness;
    double frontline_fit;
    double maintenance;
    double equity;
    double public_value;
};

struct Scored {
    std::string name;
    double readiness;
    double absorption;
    double public_value_priority;
    double sequencing_need;
    double portfolio_score;
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

double readiness(const Option& x) {
    return 0.14*x.desirability + 0.13*x.authority + 0.12*x.capability +
           0.10*x.funding + 0.10*x.policy_fit + 0.11*x.governance +
           0.08*x.trust_gain + 0.08*x.burden_reduction + 0.06*x.data_readiness +
           0.05*x.frontline_fit + 0.03*x.maintenance -
           0.05*x.coordination - 0.05*x.implementation_risk;
}

double absorption(const Option& x) {
    return 0.18*x.authority + 0.18*x.capability + 0.14*x.funding +
           0.14*x.governance + 0.12*x.policy_fit + 0.10*x.frontline_fit +
           0.08*x.maintenance + 0.06*x.data_readiness;
}

double public_value_priority(const Option& x) {
    return 0.24*x.public_value + 0.20*x.burden_reduction + 0.18*x.trust_gain +
           0.16*x.equity + 0.12*x.desirability + 0.10*x.policy_fit -
           0.08*x.implementation_risk;
}

double sequencing_need(const Option& x) {
    return 0.28*x.coordination + 0.24*x.implementation_risk +
           0.14*(10.0-x.authority) + 0.12*(10.0-x.capability) +
           0.10*(10.0-x.funding) + 0.07*(10.0-x.maintenance) +
           0.05*(10.0-x.data_readiness);
}

double portfolio_score(const Option& x) {
    return 0.30*readiness(x) + 0.26*public_value_priority(x) +
           0.20*absorption(x) + 0.10*x.equity + 0.06*x.trust_gain -
           0.12*sequencing_need(x) - 0.08*x.implementation_risk;
}

std::vector<Option> read_options(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Option> options;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 17) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        options.push_back(
            Option{
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
                to_double(fields[16])
            }
        );
    }

    return options;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/institutional_design_options_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto options = read_options(input_path);
        std::vector<Scored> scored;

        for (const auto& option : options) {
            scored.push_back(
                Scored{
                    option.name,
                    readiness(option),
                    absorption(option),
                    public_value_priority(option),
                    sequencing_need(option),
                    portfolio_score(option)
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const Scored& a, const Scored& b) {
                return a.portfolio_score > b.portfolio_score;
            }
        );

        std::cout << "rank,option,change_readiness,absorption_capacity,public_value_priority,sequencing_need,portfolio_score\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].readiness << ","
                      << scored[i].absorption << ","
                      << scored[i].public_value_priority << ","
                      << scored[i].sequencing_need << ","
                      << scored[i].portfolio_score << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
