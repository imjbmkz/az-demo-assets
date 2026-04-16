-- Create schema

--for storing control tables used in pipelines
create schema ctrl_fw 
go

--for storing staging tables / landing zone of ingested data
create schema staging
go

--for storing cleaned and historical data
create schema cleaned
go

--for storing the curated data for reporting purposes
create schema curated
go