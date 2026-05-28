use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct StrategicOption {
    name: String,
    desirability: f64,
    feasibility: f64,
    viability: f64,
    alignment: f64,
    ethics: f64,
    learning: f64,
    effort: f64,
    risk: f64,
    capability_gap: f64,
    evidence: f64,
    time_to_learn: f64,
    public_value: f64,
}

#[derive(Debug)]
struct ScoredOption {
    name: String,
    score: f64,
    portfolio_value: f64,
    risk: f64,
}

fn strategic_score(x: &StrategicOption) -> f64 {
    0.17 * x.desirability
        + 0.13 * x.feasibility
        + 0.13 * x.viability
        + 0.16 * x.alignment
        + 0.11 * x.ethics
        + 0.10 * x.learning
        + 0.08 * x.public_value
        + 0.05 * x.evidence * 10.0
        - 0.03 * x.risk
        - 0.02 * x.effort
        - 0.01 * x.capability_gap
        - 0.01 * x.time_to_learn
}

fn portfolio_value(x: &StrategicOption) -> f64 {
    strategic_score(x) + 0.30 * x.learning + 0.20 * x.public_value + 0.15 * x.evidence * 10.0
        - 0.22 * x.risk - 0.14 * x.effort - 0.10 * x.capability_gap
}

fn parse_options(path: &str) -> Result<Vec<StrategicOption>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut items = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 15 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        items.push(StrategicOption {
            name: fields[0].trim().to_string(),
            desirability: fields[3].trim().parse()?,
            feasibility: fields[4].trim().parse()?,
            viability: fields[5].trim().parse()?,
            alignment: fields[6].trim().parse()?,
            ethics: fields[7].trim().parse()?,
            learning: fields[8].trim().parse()?,
            effort: fields[9].trim().parse()?,
            risk: fields[10].trim().parse()?,
            capability_gap: fields[11].trim().parse()?,
            evidence: fields[12].trim().parse()?,
            time_to_learn: fields[13].trim().parse()?,
            public_value: fields[14].trim().parse()?,
        });
    }

    Ok(items)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/strategic_options_raw.csv".to_string());

    let options = parse_options(&path)?;

    let mut scored: Vec<ScoredOption> = options
        .iter()
        .map(|x| ScoredOption {
            name: x.name.clone(),
            score: strategic_score(x),
            portfolio_value: portfolio_value(x),
            risk: x.risk,
        })
        .collect();

    scored.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());

    println!("rank,option,strategic_score,portfolio_value,strategic_risk");
    for (idx, row) in scored.iter().enumerate() {
        println!(
            "{},{},{:.6},{:.6},{:.6}",
            idx + 1,
            row.name,
            row.score,
            row.portfolio_value,
            row.risk
        );
    }

    Ok(())
}
