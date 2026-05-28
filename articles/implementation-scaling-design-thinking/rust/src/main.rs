use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Intervention {
    name: String,
    adoption_readiness: f64,
    operational_fit: f64,
    durability: f64,
    governance_readiness: f64,
    equity_readiness: f64,
    financial_sustainability: f64,
    operational_risk: f64,
    governance_risk: f64,
    technical_risk: f64,
    equity_risk: f64,
    financial_risk: f64,
}

#[derive(Debug)]
struct ScoredIntervention {
    name: String,
    value: f64,
    risk: f64,
}

fn composite_risk(x: &Intervention) -> f64 {
    0.25 * x.operational_risk
        + 0.22 * x.governance_risk
        + 0.18 * x.technical_risk
        + 0.22 * x.equity_risk
        + 0.13 * x.financial_risk
}

fn implementation_value(x: &Intervention) -> f64 {
    0.20 * x.adoption_readiness
        + 0.18 * x.operational_fit
        + 0.18 * x.durability
        + 0.15 * x.governance_readiness
        + 0.14 * x.equity_readiness
        + 0.10 * x.financial_sustainability
        - 0.05 * composite_risk(x)
}

fn parse_portfolio(path: &str) -> Result<Vec<Intervention>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut interventions = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 14 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        interventions.push(Intervention {
            name: fields[0].trim().to_string(),
            adoption_readiness: fields[3].trim().parse()?,
            operational_fit: fields[4].trim().parse()?,
            durability: fields[5].trim().parse()?,
            governance_readiness: fields[6].trim().parse()?,
            equity_readiness: fields[7].trim().parse()?,
            financial_sustainability: fields[8].trim().parse()?,
            operational_risk: fields[9].trim().parse()?,
            governance_risk: fields[10].trim().parse()?,
            technical_risk: fields[11].trim().parse()?,
            equity_risk: fields[12].trim().parse()?,
            financial_risk: fields[13].trim().parse()?,
        });
    }

    Ok(interventions)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/implementation_portfolio_raw.csv".to_string());

    let interventions = parse_portfolio(&path)?;
    let mut scored: Vec<ScoredIntervention> = interventions
        .iter()
        .map(|x| ScoredIntervention {
            name: x.name.clone(),
            value: implementation_value(x),
            risk: composite_risk(x),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,intervention,implementation_value,composite_risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
