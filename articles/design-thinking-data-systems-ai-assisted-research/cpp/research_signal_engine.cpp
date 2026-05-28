#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct ResearchSignal {
    std::string name;
    double source_strength;
    double relevance;
    double traceability;
    double representativeness;
    double validation;
    double missingness;
    double ai_assistance_risk;
    double decision_relevance;
    double recency;
    double consent;
    double coverage;
};

struct ScoredSignal {
    std::string name;
    double confidence;
    double bias_risk;
    double ai_risk;
    double decision_readiness;
    double governance_priority;
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

double confidence(const ResearchSignal& x) {
    return 0.18*x.source_strength + 0.17*x.relevance + 0.15*x.traceability +
           0.15*x.representativeness + 0.15*x.validation + 0.08*x.recency +
           0.07*x.consent + 0.05*x.coverage;
}

double bias_risk(const ResearchSignal& x) {
    return 0.26*x.missingness + 0.22*(1.0-x.representativeness) +
           0.18*(1.0-x.validation) + 0.14*x.ai_assistance_risk +
           0.10*(1.0-x.traceability) + 0.10*(1.0-x.coverage);
}

double ai_risk(const ResearchSignal& x) {
    return 0.38*x.ai_assistance_risk + 0.18*(1.0-x.traceability) +
           0.16*(1.0-x.validation) + 0.14*x.missingness + 0.14*(1.0-x.consent);
}

double decision_readiness(const ResearchSignal& x) {
    const double c = confidence(x);
    const double b = bias_risk(x);
    double value = 0.30*c + 0.24*x.decision_relevance + 0.14*x.validation +
                   0.12*x.traceability + 0.08*x.consent + 0.08*x.coverage -
                   0.04*b;
    if (value < 0.0) return 0.0;
    if (value > 1.0) return 1.0;
    return value;
}

std::vector<ResearchSignal> read_signals(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<ResearchSignal> signals;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 13) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        signals.push_back(
            ResearchSignal{
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
                to_double(fields[12])
            }
        );
    }

    return signals;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/research_signals_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto signals = read_signals(input_path);
        std::vector<ScoredSignal> scored;

        for (const auto& signal : signals) {
            const double c = confidence(signal);
            const double b = bias_risk(signal);
            const double a = ai_risk(signal);
            const double d = decision_readiness(signal);
            const double g = 0.24*b + 0.22*a + 0.16*(1.0-signal.traceability) +
                             0.14*(1.0-signal.consent) + 0.12*(1.0-signal.validation) +
                             0.12*signal.decision_relevance;

            scored.push_back(ScoredSignal{signal.name, c, b, a, d, g});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredSignal& x, const ScoredSignal& y) {
                return x.governance_priority > y.governance_priority;
            }
        );

        std::cout << "rank,signal,confidence_score,bias_risk,ai_risk,decision_readiness,governance_priority\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].confidence << ","
                      << scored[i].bias_risk << ","
                      << scored[i].ai_risk << ","
                      << scored[i].decision_readiness << ","
                      << scored[i].governance_priority << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
