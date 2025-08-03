# Advanced CDK Constructs

[![codecov](https://codecov.io/gh/spensireli/advanced-cdk-constructs/graph/badge.svg?token=50IITI207T)](https://codecov.io/gh/spensireli/advanced-cdk-constructs)

A collection of advanced AWS CDK constructs to simplify AWS.

## Installation

### From NPM

```bash
npm install advanced-cdk-constructs
```

### From GitHub

```bash
npm install git+https://github.com/spensireli/advanced-cdk-constructs.git
```

## Available Constructs

### GuardDuty Construct

The `GuardDutyConstruct` provides a simplified way to deploy AWS GuardDuty with common security configurations.

#### Import

```python
import { GuardDutyConstruct, GuardDutyConstructProps } from 'advanced-cdk-constructs';
```

#### Basic Usage

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { GuardDutyConstruct } from 'advanced-cdk-constructs';

export class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create GuardDuty with default settings
    const guardDuty = new GuardDutyConstruct(this, 'MyGuardDuty');
  }
}
```

#### Advanced Configuration

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { GuardDutyConstruct, GuardDutyConstructProps } from 'advanced-cdk-constructs';

export class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const guardDutyProps: GuardDutyConstructProps = {
      enableGuardDuty: true,
      kubernetesAuditLogs: true,
      malwareProtection: true,
      s3Logs: true,
    };

    const guardDuty = new GuardDutyConstruct(this, 'MyGuardDuty', guardDutyProps);

    // Access the detector ID for other resources
    console.log('GuardDuty Detector ID:', guardDuty.detectorId);
  }
}
```

#### Configuration Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enableGuardDuty` | `boolean` | `true` | Whether to enable GuardDuty |
| `kubernetesAuditLogs` | `boolean` | `true` | Enable Kubernetes audit logs monitoring |
| `malwareProtection` | `boolean` | `true` | Enable malware protection for EC2 instances |
| `s3Logs` | `boolean` | `true` | Enable S3 logs monitoring |

#### Features

* **Runtime Monitoring**: Automatically enabled for comprehensive threat detection
* **Kubernetes Audit Logs**: Monitors Kubernetes cluster activities
* **Malware Protection**: Scans EC2 instances for malware
* **S3 Logs Monitoring**: Monitors S3 bucket activities for suspicious behavior
* **Detector ID Access**: Public property to reference the detector in other constructs

## Development

### Prerequisites

* Node.js 22.0.0 or higher
* AWS CDK CLI
* TypeScript

### Setup

1. Clone the repository:

```bash
git clone git@github.com:spensireli/advanced-cdk-constructs.git
cd advanced-cdk-constructs
```

1. Install dependencies:

```bash
npm install
```

1. Build the project:

```bash
npx projen build
```

### Testing

Run the test suite:

```bash
npx projen test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/spensireli/advanced-cdk-constructs).
