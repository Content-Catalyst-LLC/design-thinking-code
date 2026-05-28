use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Experiment {
    name: String,
    learning_gain: f64,
    update_flexibility: f64,
    expected_improvement: f64,
    residual_risk: f64,
}

#[derive(Debug)]
struct ScoredExperiment {
    name: String,
    value: f64,
}

fn experiment_value(experiment: &Experiment) -> f64 {
    0.35 * experiment.learning_gain
        + 0.25 * experiment.update_flexibility
        + 0.25 * experiment.expected_improvement
        - 0.15 * experiment.residual_risk
}

fn parse_experiments(path: &str) -> Result<Vec<Experiment>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut experiments = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 5 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        experiments.push(Experiment {
            name: fields[0].trim().to_string(),
            learning_gain: fields[1].trim().parse()?,
            update_flexibility: fields[2].trim().parse()?,
            expected_improvement: fields[3].trim().parse()?,
            residual_risk: fields[4].trim().parse()?,
        });
    }

    Ok(experiments)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/experiments_raw.csv".to_string());

    let experiments = parse_experiments(&path)?;
    let mut scored: Vec<ScoredExperiment> = experiments
        .iter()
        .map(|e| ScoredExperiment {
            name: e.name.clone(),
            value: experiment_value(e),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,experiment,experiment_value");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6}", idx + 1, row.name, row.value);
    }

    Ok(())
}
