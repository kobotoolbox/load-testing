use goose::prelude::*;
use goose::GooseAttack;
use xmltree::Element;

const FORM_UID: &str = "YOUR_FORM_UID"; // Replace with your actual form UID
const API_TOKEN: &str = "YOUR_API_TOKEN"; // Replace with your actual API token
const KPI_SUBDOMAIN: &str = "kf";
const ENKETO_SUBDOMAIN: &str = "ee";

const SMALL_FILE: &str = "assets/small.txt";
const IMAGE_FILE: &str = "assets/image.png";

async fn loadtest_index(user: &mut GooseUser) -> TransactionResult {
    let _goose_metrics = user.get("").await?;
    Ok(())
}

async fn simulate_unnecessary_interactions(user: &mut GooseUser) -> TransactionResult {
    user.get(&format!("/x/{FORM_UID}")).await?;
    // user.get(&self.check_connection_url).await?;
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), GooseError> {
    GooseAttack::initialize()?
        .register_scenario(
            scenario!("LoadtestTransactions")
                .register_transaction(transaction!(loadtest_index))
                .register_transaction(transaction!(simulate_unnecessary_interactions)),
        )
        .execute()
        .await?;

    Ok(())
}
