-- Initialize database with basic schema and indexes
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_niche ON campaigns(product_niche);
CREATE INDEX IF NOT EXISTS idx_creators_niche ON creators(niche);
CREATE INDEX IF NOT EXISTS idx_creators_platform ON creators(platform);
CREATE INDEX IF NOT EXISTS idx_negotiations_campaign ON negotiations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_negotiations_creator ON negotiations(creator_id);
CREATE INDEX IF NOT EXISTS idx_contracts_campaign ON contracts(campaign_id);
CREATE INDEX IF NOT EXISTS idx_outreach_logs_campaign ON outreach_logs(campaign_id);

-- Create functions for updated timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for automatic timestamp updates
CREATE TRIGGER update_campaigns_updated_at 
    BEFORE UPDATE ON campaigns 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();