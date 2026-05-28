use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Intervention {
    name: String,
    human_value: f64,
    system_leverage: f64,
    feasibility: f64,
    equity_sensitivity: f64,
    durability: f64,
    risk: f64,
}

#[derive(Debug)]
struct ScoredIntervention {
    name: String,
    value: f64,
    risk: f64,
}

fn system_design_value(x: &Intervention) -> f64 {
    0.24 * x.human_value
        + 0.26 * x.system_leverage
        + 0.18 * x.feasibility
        + 0.14 * x.equity_sensitivity
        + 0.12 * x.durability
        - 0.06 * x.risk
}

fn parse_portfolio(path: &str) -> Result<Vec<Intervention>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut interventions = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 9 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        interventions.push(Intervention {
            name: fields[0].trim().to_string(),
            human_value: fields[3].trim().parse()?,
            system_leverage: fields[4].trim().parse()?,
            feasibility: fields[5].trim().parse()?,
            equity_sensitivity: fields[6].trim().parse()?,
            durability: fields[7].trim().parse()?,
            risk: fields[8].trim().parse()?,
        });
    }

    Ok(interventions)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/system_intervention_portfolio_raw.csv".to_string());

    let interventions = parse_portfolio(&path)?;
    let mut scored: Vec<ScoredIntervention> = interventions
        .iter()
        .map(|x| ScoredIntervention {
            name: x.name.clone(),
            value: system_design_value(x),
            risk: x.risk,
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,intervention,system_design_value,risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
