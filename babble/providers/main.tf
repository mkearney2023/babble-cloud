terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "= 4.52.0"
        }
        archive = {
            source = "hashicorp/archive"
            version = "= 2.3.0"
        }
        local = {
            source = "hashicorp/local"
            version = "= 2.3.0"
        }
    }
}