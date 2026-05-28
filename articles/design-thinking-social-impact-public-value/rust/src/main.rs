use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Intervention {
    name: String,
    access: f64,
    equity: f64,
    dignity: f64,
    legitimacy: f64,
    accountability: f64,
    outcome_strength: f64,
    sustainability: f64,
    learning: f64,
    feasibility: f64,
    governance: f64,
    implementation_risk: f64,
    burden_risk: f64,
    participation: f64,
    community_value: f64,
    repair: f64,
    stewardship: f64,
}

#[derive(Debug)]
struct Scored {
    name: String,
    public_value: f64,
    readiness: f64,
    stewardship_need: f64,
    portfolio_priority: f64,
}

fn public_value(x: &Intervention) -> f64 {
    0.13*x.access + 0.15*x.equity + 0.12*x.dignity +
    0.12*x.legitimacy + 0.13*x.accountability + 0.11*x.outcome_strength +
    0.08*x.sustainability + 0.07*x.learning + 0.05*x.community_value +
    0.04*x.repair
}

fn impact_readiness(x: &Intervention) -> f64 {
    let pv = public_value(x);
    0.30*pv + 0.17*x.feasibility + 0.16*x.governance +
    0.12*x.learning + 0.10*x.participation + 0.08*x.stewardship +
    0.07*x.repair - 0.07*x.implementation_risk - 0.07*x.burden_risk
}

fn stewardship_need(x: &Intervention) -> f64 {
    0.24*x.implementation_risk + 0.22*x.burden_risk +
    0.16*(10.0-x.governance) + 0.12*(10.0-x.sustainability) +
    0.10*(10.0-x.learning) + 0.08*(10.0-x.repair) +
    0.08*(10.0-x.stewardship)
}

fn portfolio_priority(x: &Intervention) -> f64 {
    0.36*public_value(x) + 0.28*impact_readiness(x) +
    0.14*x.equity + 0.10*x.community_value + 0.06*x.participation -
    0.14*stewardship_need(x) - 0.06*x.implementation_risk
}

fn parse_interventions(path: &str) -> Result<Vec<Intervention>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut items = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 18 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        items.push(Intervention {
            name: fields[0].trim().to_string(),
            access: fields[2].trim().parse()?,
            equity: fields[3].trim().parse()?,
            dignity: fields[4].trim().parse()?,
            legitimacy: fields[5].trim().parse()?,
            accountability: fields[6].trim().parse()?,
            outcome_strength: fields[7].trim().parse()?,
            sustainability: fields[8].trim().parse()?,
            learning: fields[9].trim().parse()?,
            feasibility: fields[10].trim().parse()?,
            governance: fields[11].trim().parse()?,
            implementation_risk: fields[12].trim().parse()?,
            burden_risk: fields[13].trim().parse()?,
            participation: fields[14].trim().parse()?,
            community_value: fields[15].trim().parse()?,
            repair: fields[16].trim().parse()?,
            stewardship: fields[17].trim().parse()?,
        });
    }

    Ok(items)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/social_impact_interventions_raw.csv".to_string());

    let interventions = parse_interventions(&path)?;

    let mut scored: Vec<Scored> = interventions
        .iter()
        .map(|x| Scored {
            name: x.name.clone(),
            public_value: public_value(x),
            readiness: impact_readiness(x),
            stewardship_need: stewardship_need(x),
            portfolio_priority: portfolio_priority(x),
        })
        .collect();

    scored.sort_by(|a, b| b.portfolio_priority.partial_cmp(&a.portfolio_priority).unwrap());

    println!("rank,intervention,public_value_score,impact_readiness,stewardship_need,portfolio_priority");
    for (idx, row) in scored.iter().enumerate() {
        println!(
            "{},{},{:.6},{:.6},{:.6},{:.6}",
            idx + 1,
            row.name,
            row.public_value,
            row.readiness,
            row.stewardship_need,
            row.portfolio_priority
        );
    }

    Ok(())
}
