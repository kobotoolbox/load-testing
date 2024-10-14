use goose::prelude::*;

async fn loadtest_index(user: &mut GooseUser) -> TransactionResult {
    let _goose_metrics = user.get("").await?;

    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), GooseError> {
    GooseAttack::initialize()?
        .register_scenario(scenario!("LoadtestTransactions")
            .register_transaction(transaction!(loadtest_index))
        )
        .execute()
        .await?;

    Ok(())
}
