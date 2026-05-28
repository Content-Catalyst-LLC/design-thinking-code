use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Prototype {
    name: String,
    learning_gain: f64,
    feasibility_signal: f64,
    user_response: f64,
    equity_value: f64,
    implementation_relevance: f64,
    ethical_risk: f64,
    operational_risk: f64,
    technical_risk: f64,
    scaling_risk: f64,
}

#[derive(Debug)]
struct ScoredPrototype {
    name: String,
    value: f64,
    risk: f64,
}

fn composite_risk(p: &Prototype) -> f64 {
    0.30 * p.ethical_risk
        + 0.30 * p.operational_risk
        + 0.20 * p.technical_risk
        + 0.20 * p.scaling_risk
}

fn prototype_value(p: &Prototype) -> f64 {
    0.25 * p.learning_gain
        + 0.18 * p.feasibility_signal
        + 0.20 * p.user_response
        + 0.15 * p.equity_value
        + 0.12 * p.implementation_relevance
        - 0.10 * composite_risk(p)
}

fn parse_portfolio(path: &str) -> Result<Vec<Prototype>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut prototypes = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 12 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        prototypes.push(Prototype {
            name: fields[0].trim().to_string(),
            learning_gain: fields[3].trim().parse()?,
            feasibility_signal: fields[4].trim().parse()?,
            user_response: fields[5].trim().parse()?,
            equity_value: fields[6].trim().parse()?,
            implementation_relevance: fields[7].trim().parse()?,
            ethical_risk: fields[8].trim().parse()?,
            operational_risk: fields[9].trim().parse()?,
            technical_risk: fields[10].trim().parse()?,
            scaling_risk: fields[11].trim().parse()?,
        });
    }

    Ok(prototypes)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/prototype_portfolio_raw.csv".to_string());

    let prototypes = parse_portfolio(&path)?;
    let mut scored: Vec<ScoredPrototype> = prototypes
        .iter()
        .map(|p| ScoredPrototype {
            name: p.name.clone(),
            value: prototype_value(p),
            risk: composite_risk(p),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,prototype,prototype_value,composite_risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
