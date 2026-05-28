use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Intervention {
    name: String,
    outcome_improvement: f64,
    burden_reduction: f64,
    equity_performance: f64,
    trust_improvement: f64,
    durability: f64,
    operational_cost: f64,
    residual_risk: f64,
}

#[derive(Debug)]
struct ScoredIntervention {
    name: String,
    value: f64,
    penalty: f64,
}

fn penalty(x: &Intervention) -> f64 {
    0.50 * x.operational_cost + 0.50 * x.residual_risk
}

fn evaluation_value(x: &Intervention) -> f64 {
    0.24 * x.outcome_improvement
        + 0.20 * x.burden_reduction
        + 0.20 * x.equity_performance
        + 0.16 * x.trust_improvement
        + 0.14 * x.durability
        - 0.06 * penalty(x)
}

fn parse_portfolio(path: &str) -> Result<Vec<Intervention>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut interventions = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 10 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        interventions.push(Intervention {
            name: fields[0].trim().to_string(),
            outcome_improvement: fields[3].trim().parse()?,
            burden_reduction: fields[4].trim().parse()?,
            equity_performance: fields[5].trim().parse()?,
            trust_improvement: fields[6].trim().parse()?,
            durability: fields[7].trim().parse()?,
            operational_cost: fields[8].trim().parse()?,
            residual_risk: fields[9].trim().parse()?,
        });
    }

    Ok(interventions)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/evaluation_portfolio_raw.csv".to_string());

    let interventions = parse_portfolio(&path)?;
    let mut scored: Vec<ScoredIntervention> = interventions
        .iter()
        .map(|x| ScoredIntervention {
            name: x.name.clone(),
            value: evaluation_value(x),
            penalty: penalty(x),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,intervention,evaluation_value,penalty");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.penalty);
    }

    Ok(())
}
