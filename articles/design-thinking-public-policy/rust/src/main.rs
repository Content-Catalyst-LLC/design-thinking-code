use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct PolicyPilot {
    name: String,
    accessibility: f64,
    feasibility: f64,
    legitimacy: f64,
    equity: f64,
    burden_reduction: f64,
    durability: f64,
    risk: f64,
}

#[derive(Debug)]
struct ScoredPilot {
    name: String,
    value: f64,
    risk: f64,
}

fn policy_value(x: &PolicyPilot) -> f64 {
    0.20 * x.accessibility
        + 0.16 * x.feasibility
        + 0.16 * x.legitimacy
        + 0.20 * x.equity
        + 0.14 * x.burden_reduction
        + 0.08 * x.durability
        - 0.06 * x.risk
}

fn parse_pilots(path: &str) -> Result<Vec<PolicyPilot>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut pilots = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 10 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        pilots.push(PolicyPilot {
            name: fields[0].trim().to_string(),
            accessibility: fields[3].trim().parse()?,
            feasibility: fields[4].trim().parse()?,
            legitimacy: fields[5].trim().parse()?,
            equity: fields[6].trim().parse()?,
            burden_reduction: fields[7].trim().parse()?,
            durability: fields[8].trim().parse()?,
            risk: fields[9].trim().parse()?,
        });
    }

    Ok(pilots)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/public_policy_pilots_raw.csv".to_string());

    let pilots = parse_pilots(&path)?;
    let mut scored: Vec<ScoredPilot> = pilots
        .iter()
        .map(|x| ScoredPilot {
            name: x.name.clone(),
            value: policy_value(x),
            risk: x.risk,
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,pilot,policy_value,risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
