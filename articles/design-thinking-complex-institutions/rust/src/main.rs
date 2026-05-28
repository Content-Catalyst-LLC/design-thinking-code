use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct OptionItem {
    name: String,
    desirability: f64,
    authority: f64,
    capability: f64,
    funding: f64,
    policy_fit: f64,
    governance: f64,
    trust_gain: f64,
    burden_reduction: f64,
    coordination: f64,
    implementation_risk: f64,
    data_readiness: f64,
    frontline_fit: f64,
    maintenance: f64,
    equity: f64,
    public_value: f64,
}

#[derive(Debug)]
struct Scored {
    name: String,
    readiness: f64,
    absorption: f64,
    public_value_priority: f64,
    sequencing_need: f64,
    portfolio_score: f64,
}

fn readiness(x: &OptionItem) -> f64 {
    0.14*x.desirability + 0.13*x.authority + 0.12*x.capability +
    0.10*x.funding + 0.10*x.policy_fit + 0.11*x.governance +
    0.08*x.trust_gain + 0.08*x.burden_reduction + 0.06*x.data_readiness +
    0.05*x.frontline_fit + 0.03*x.maintenance -
    0.05*x.coordination - 0.05*x.implementation_risk
}

fn absorption(x: &OptionItem) -> f64 {
    0.18*x.authority + 0.18*x.capability + 0.14*x.funding +
    0.14*x.governance + 0.12*x.policy_fit + 0.10*x.frontline_fit +
    0.08*x.maintenance + 0.06*x.data_readiness
}

fn public_value_priority(x: &OptionItem) -> f64 {
    0.24*x.public_value + 0.20*x.burden_reduction + 0.18*x.trust_gain +
    0.16*x.equity + 0.12*x.desirability + 0.10*x.policy_fit -
    0.08*x.implementation_risk
}

fn sequencing_need(x: &OptionItem) -> f64 {
    0.28*x.coordination + 0.24*x.implementation_risk +
    0.14*(10.0-x.authority) + 0.12*(10.0-x.capability) +
    0.10*(10.0-x.funding) + 0.07*(10.0-x.maintenance) +
    0.05*(10.0-x.data_readiness)
}

fn portfolio_score(x: &OptionItem) -> f64 {
    0.30*readiness(x) + 0.26*public_value_priority(x) +
    0.20*absorption(x) + 0.10*x.equity + 0.06*x.trust_gain -
    0.12*sequencing_need(x) - 0.08*x.implementation_risk
}

fn parse_options(path: &str) -> Result<Vec<OptionItem>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut items = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 17 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        items.push(OptionItem {
            name: fields[0].trim().to_string(),
            desirability: fields[2].trim().parse()?,
            authority: fields[3].trim().parse()?,
            capability: fields[4].trim().parse()?,
            funding: fields[5].trim().parse()?,
            policy_fit: fields[6].trim().parse()?,
            governance: fields[7].trim().parse()?,
            trust_gain: fields[8].trim().parse()?,
            burden_reduction: fields[9].trim().parse()?,
            coordination: fields[10].trim().parse()?,
            implementation_risk: fields[11].trim().parse()?,
            data_readiness: fields[12].trim().parse()?,
            frontline_fit: fields[13].trim().parse()?,
            maintenance: fields[14].trim().parse()?,
            equity: fields[15].trim().parse()?,
            public_value: fields[16].trim().parse()?,
        });
    }

    Ok(items)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/institutional_design_options_raw.csv".to_string());

    let options = parse_options(&path)?;

    let mut scored: Vec<Scored> = options
        .iter()
        .map(|x| Scored {
            name: x.name.clone(),
            readiness: readiness(x),
            absorption: absorption(x),
            public_value_priority: public_value_priority(x),
            sequencing_need: sequencing_need(x),
            portfolio_score: portfolio_score(x),
        })
        .collect();

    scored.sort_by(|a, b| b.portfolio_score.partial_cmp(&a.portfolio_score).unwrap());

    println!("rank,option,change_readiness,absorption_capacity,public_value_priority,sequencing_need,portfolio_score");
    for (idx, row) in scored.iter().enumerate() {
        println!(
            "{},{},{:.6},{:.6},{:.6},{:.6},{:.6}",
            idx + 1,
            row.name,
            row.readiness,
            row.absorption,
            row.public_value_priority,
            row.sequencing_need,
            row.portfolio_score
        );
    }

    Ok(())
}
