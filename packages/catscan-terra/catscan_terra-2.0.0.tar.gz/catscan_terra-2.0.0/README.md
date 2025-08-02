# CatSCAN v2.0 🐾

**Terraform Cloud multi-workspace scanner with retro vibes**

CatSCAN is a secure, high-performance CLI tool that uses the Terraform Cloud API to scan all workspaces in your organization and display a comprehensive summary of resources. Built for platform and DevOps engineers who want secure, high-performance visibility across all Terraform workspaces.

CatSCAN uses the [Terraform Cloud API v2](https://developer.hashicorp.com/terraform/cloud-docs/api-docs) for authentication, workspace queries, and state analysis.

Follow the launch post on LinkedIn for discussion and feature requests.

---

##  Features

### Core Functionality
* **Comprehensive Scanning** - Fetches all workspaces from Terraform Cloud with pagination support
* **Deep State Analysis** - Downloads and parses state files (JSON/ZIP) with nested module support
* **Resource Discovery** - Counts and categorizes all resource types across workspaces
* **Parallel Processing** - Multi-threaded scanning with configurable worker pools
* **Connection Pooling** - Efficient HTTP session management for faster API calls

### Security & Authentication
*  **Keyring Integration** - Secure credential storage using system keyring (encrypted)
*  **Multiple Auth Methods** - Environment variables, keyring, or interactive input
*  **Input Validation** - Sanitization of organization names and API tokens
*  **Credential Management** - Built-in UI for updating/deleting stored tokens

### User Interface
*  **Retro ASCII Art** - Old-school terminal aesthetics for the modern DevOps warrior
*  **Rich Terminal UI** - Beautiful tables and panels powered by Rich library
*  **Cross-Platform** - Native support for Windows, macOS, and Linux
*  **Curses Mode** - Buttery-smooth navigation on Linux terminals

### Data & History
*  **Historical Tracking** - Maintains scan history with detailed resource breakdowns
*  **Interactive History Browser** - Navigate past scans with arrow keys
*  **Persistent Storage** - Scan results saved in JSON format
*  **Detailed Views** - Drill down into specific scans and workspace resources

---

## 📦 Installation

### From GitHub (Recommended for v2.0)

```bash
git clone https://github.com/cloudsifar/catscan-2.0.git
cd catscan-2.0
pip install -e .
```

### From PyPI

```bash
pip install catscan-terra
```

---

## 🎮 Usage

### Basic Commands

```bash
# Run CatSCAN with default settings
catscan

# Enable debug logging
catscan --debug

# Custom log file
catscan --log-file /path/to/catscan.log

# Skip the ASCII banner (for automation)
catscan --no-banner
```

### Authentication Methods

#### Method 1: Secure Keyring Storage (Recommended)

On first run, CatSCAN will prompt for your credentials and offer to store them securely:

```
🔒 Secure Configuration Setup
   ✅ Keyring available - credentials will be stored securely
   Your token will be encrypted in the system credential store

Organization name: my-terraform-org
Terraform Cloud API Token: **********************
💾 Save token securely to system keyring? (Y/n): y
```

#### Method 2: Environment Variables

For CI/CD pipelines or automation:

```bash
export TFC_ORG_NAME="my-terraform-org"
export TFC_TOKEN="your-api-token-here"
catscan
```

**Security Tips for Environment Variables:**
- Never commit `.env` files to version control
- Use CI/CD secret management features
- On Linux/Mac: Add to `~/.bashrc` or `~/.zshrc` with restricted permissions
- On Windows: Use User Environment Variables (not System)
- Consider using tools like `direnv` or `dotenv` for project-specific variables

#### Method 3: Interactive Input

Simply run `catscan` without any configuration, and it will guide you through setup.

---

## 🎯 Menu Navigation

### Main Scan Results Menu

After completing a scan, you'll see:

```
╭────────────────────────────────────────────────────────────────╮
│   What would you like to do?                                   │
│                                                                │
│   ╭─────────────────────────────╮                              │
│   │ [D] View detailed results   │  ← See all resources by type │
│   │ [H] View scan history       │  ← Browse previous scans     │
│   │ [R] Run another scan        │  ← Refresh data              │
│   │ [S] Security settings       │  ← Manage stored credentials │
│   │ [P] Platform info (debug)   │  ← Troubleshooting info      │
│   │ [Q] Quit                    │                              │
│   ╰─────────────────────────────╯                              │
╰────────────────────────────────────────────────────────────────╯
```

### History Browser Controls

- **↑/↓** - Navigate through scan history
- **Enter** - View detailed scan results
- **Escape** - Return to main menu
- **Page Up/Down** - Jump through pages (Linux/curses mode)

### Credential Manager

Access via `[S] Security settings`:
- View all organizations with stored tokens
- Verify token validity
- Update expired tokens
- Delete stored credentials

---

## 📊 Example Output

### Scan Summary
```
Found 42 workspaces

📊 Deployed Resources by Workspace (acme-corp)
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Workspace          ┃ Resources                                                           ┃ Status       ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ prod-app           │ aws_instance(12), aws_db_instance(3), aws_security_group(8)         │ ✅ 23        │
│ staging            │ aws_s3_bucket(5), aws_lambda_function(8)                            │ ✅ 13        │
│ dev-a              │ aws_instance(5), aws_cloudwatch_log_group(2), aws_iam_role(3)       │ ✅ 10        │
│ dev-b              │ aws_lambda_function(6), aws_iam_policy(2), aws_sqs_queue(2)         │ ✅ 10        │
│ data-pipeline      │ aws_glue_job(4), aws_glue_catalog_table(2), aws_s3_bucket(2)        │ ✅ 8         │
│ billing-analytics  │ aws_athena_database(1), aws_athena_table(2), aws_s3_bucket(2)       │ ✅ 5         │
│ security-hub       │ aws_guardduty_detector(1), aws_securityhub_standards_subscription(2)│ ✅ 3         │
│ dev-c              │ aws_instance(4), aws_ecr_repository(3), aws_codebuild_project(2)    │ ✅ 9         │
│ qa-env             │ aws_instance(3), aws_rds_cluster(2), aws_elasticache_cluster(1)     │ ✅ 6         │
│ prod-infra         │ aws_nat_gateway(2), aws_route_table(3), aws_vpc(1)                  │ ✅ 6         │
│ devops             │ aws_codepipeline(2), aws_codebuild_project(2), aws_iam_role(2)      │ ✅ 6         │
│ ml-models          │ aws_sagemaker_model(3), aws_s3_bucket(2), aws_lambda_function(2)    │ ✅ 7         │
│ iot-core           │ aws_iot_thing(5), aws_lambda_function(3), aws_dynamodb_table(2)     │ ✅ 10        │
│ user-auth          │ aws_cognito_user_pool(2), aws_lambda_function(2), aws_iam_role(1)   │ ✅ 5         │
│ prod-db            │ aws_rds_cluster(3), aws_db_subnet_group(1), aws_kms_key(1)          │ ✅ 5         │
│ legacy-archive     │ aws_s3_bucket(2), aws_glacier_vault(2)                              │ ✅ 4         │
│ sandbox            │ No state                                                            │ 🚫 No State  │
│ testing            │ No state                                                            │ 🚫 No State  │
│ temp-experiment    │ No state                                                            │ 🚫 No State  │
│ prototype-1        │ No state                                                            │ 🚫 No State  │
└────────────────────┴─────────────────────────────────────────────────────────────────────┴──────────────┘

✅ Scan Complete!
   Successfully processed: 37 workspaces  
   Empty/Error workspaces: 5  
   Total resources discovered: 159  
   ✓ Including nested modules

```

### Detailed Resource View
```
All Resources by Type and Workspace (acme-corp)
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Workspace          ┃ Resource Type              ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ prod-app           │ aws_instance               │    12 │
│                    │ aws_db_instance            │     3 │
│                    │ aws_security_group         │     8 │
│                    │ aws_iam_role               │     2 │
│                    │ aws_cloudwatch_log_group   │     1 │
│                    │ aws_elb                    │     1 │
│                    │ aws_launch_template        │     2 │
│                    │ aws_autoscaling_group      │     1 │
│                    │ aws_kms_key                │     1 │
│                    │ aws_route53_record         │     3 │
│                    │ aws_acm_certificate        │     2 │
│                    │ aws_s3_bucket              │     2 │
│                    │ aws_secretsmanager_secret  │     1 │
│ ─────────────────────────────────────────────────────── │
│ staging            │ aws_s3_bucket              │     5 │
│                    │ aws_lambda_function        │     8 │
│                    │ aws_iam_policy             │     2 │
│                    │ aws_api_gateway_rest_api   │     1 │
│                    │ aws_cloudwatch_alarm       │     3 │
│                    │ aws_dynamodb_table         │     1 │
│                    │ aws_sns_topic              │     1 │
│                    │ aws_ssm_parameter          │     2 │
└────────────────────┴────────────────────────────┴───────┘

```

---

## 🔧 Logging and Debugging

### Debug Mode

Enable comprehensive logging to troubleshoot issues:

```bash
# Logs to default location: ./catscan_YYYYMMDD_HHMMSS.log
catscan --debug

# Custom log location
catscan --log-file /var/log/catscan.log --debug
```

### Log Levels

The debug log includes:
- API request/response details
- Authentication flow
- Token verification steps
- Workspace processing progress
- Rate limiting information
- Error stack traces

### Common Issues

1. **Keyring not available**: Install with `pip install keyring`
2. **Curses UI issues**: Set `CATSCAN_NO_CURSES=true` to disable
3. **Rate limiting**: CatSCAN automatically handles Terraform Cloud rate limits
4. **SSL errors**: Check your system certificates or corporate proxy settings

---

## 🏗️ Architecture

CatSCAN v2.0 features a fully modular architecture:

```
catscan/
├── auth/          # Authentication & credential management
├── api/           # Terraform Cloud API client
├── scanner/       # Core scanning logic
├── storage/       # Data persistence
├── ui/            # Terminal user interface
└── utils/         # Cross-platform utilities
```

---

## 🤝 Contributing

I welcome suggestions and improvements! If you're new to GitHub or pull requests don't worry – here's the usual workflow:

1. **Fork the repository** on GitHub to your own account.
2. **Clone your fork** locally:
    ```bash
    git clone https://github.com/<your-username>/catscan-2.0.git
    cd catscan-2.0
    ```
3. **Create a feature branch**:
    ```bash
    git checkout -b feature/my-feature
    ```
4. **Make your changes**, then **commit** them:
    ```bash
    git add .
    git commit -m "Describe your change here"
    ```
5. **Push** the branch to your fork:
    ```bash
    git push origin feature/my-feature
    ```
6. **Open a Pull Request** against `cloudsifar/catscan-2.0` via GitHub's UI.
    * You'll automatically be notified of comments, CI results, and merge status.
    * I review and manually merge when ready.

Feel free to open **issues** first if you want to discuss big changes or report bugs.

---

## 👨‍💻 Author

**Simon Farrell** – Creator of CatSCAN and Terraform enthusiast. 

Follow me on [LinkedIn](https://www.linkedin.com/in/simon-farrell-cloud/) for updates.


---

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/license/mit).

---

## 🎸 Why CatSCAN?

Because every DevOps team needs a tool that makes infrastructure scanning feel less like work and more like playing with a retro terminal from the 80s. I was inspired because I wanted something like a cat command in bash, which scanned my workspaces and displayed it in the terminal. Plus I like cats.

```
   /\_ _/\    
  (  o.o  )   Meow! Found 42 workspaces to scan...
   )==Y==(    
  /       \   
 (  | || | )  
  \__\_/\_/__/
```