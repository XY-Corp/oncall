# Docker Build and Publish to GCP Artifact Registry

This GitHub Actions workflow automatically builds and publishes Docker images to Google Cloud Platform (GCP) Artifact Registry across multiple regions.

## Features

- **Multi-region publishing**: Supports publishing to multiple GCP Artifact Registry repositories
- **Automatic tagging**: Creates semantic version tags, branch tags, and SHA-based tags
- **Multi-platform builds**: Builds for both `linux/amd64` and `linux/arm64` architectures
- **Pull request support**: Builds images on PRs without publishing
- **Repository auto-creation**: Automatically creates Artifact Registry repositories if they don't exist
- **Build caching**: Uses GitHub Actions cache for faster builds

## Setup

### 1. GCP Service Account

Create a service account in your GCP project with the following roles:
- `Artifact Registry Writer` (minimum required for publishing)
- `Artifact Registry Administrator` (only needed if repositories don't exist and need to be auto-created)
- `Storage Admin` (for build cache)

### 2. Workload Identity Federation Setup

This is done in the devops repo in the xyai-devops-root project.
The images are in xyai-artifact-registry

Add the following secrets to your GitHub repository:

- `GCP_PROJECT_ID`: Your GCP project ID
- `WIF_PROVIDER`: The Workload Identity Provider (format: `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider`)
- `WIF_SERVICE_ACCOUNT`: The service account email (format: `SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com`)

### 4. Configure Registries

Edit the `REGISTRIES` environment variable in the workflow file to specify your target repositories:

```yaml
env:
  REGISTRIES: |
    us-central1-docker.pkg.dev/XY-Corp/oncall/oncall
    us-east1-docker.pkg.dev/XY-Corp/oncall/oncall
    europe-west1-docker.pkg.dev/XY-Corp/oncall/oncall
```

### 5. Customize Image Name

Update the `IMAGE_NAME` environment variable if you want to use a different image name:

```yaml
env:
  IMAGE_NAME: your-app-name
```

## Usage

### Automatic Triggers

The workflow runs automatically on:
- **Push to main/master**: Builds and publishes images
- **Push tags**: Creates versioned releases (e.g., `v1.0.0`)
- **Pull requests**: Builds images for testing (doesn't publish)

### Manual Triggers

You can also trigger the workflow manually from the GitHub Actions tab.

## Tagging Strategy

The workflow creates the following tags:

- **Branch tags**: `main`, `feature-branch`
- **PR tags**: `pr-123`
- **Semantic version tags**: `v1.0.0`, `v1.0`, `v1`
- **SHA tags**: `main-abc1234`
- **Latest tag**: `latest` (only on default branch)

## Output

After a successful build, the workflow will:
1. Create Artifact Registry repositories if they don't exist
2. Push images to all specified registries
3. Generate a summary with all published image URLs

## Example Output

```
## Published Images

### us-central1-docker.pkg.dev/XY-Corp/oncall/oncall
- `us-central1-docker.pkg.dev/XY-Corp/oncall/oncall:latest`
- `us-central1-docker.pkg.dev/XY-Corp/oncall/oncall:v1.0.0`
- `us-central1-docker.pkg.dev/XY-Corp/oncall/oncall:main-abc1234`

### us-east1-docker.pkg.dev/XY-Corp/oncall/oncall
- `us-east1-docker.pkg.dev/XY-Corp/oncall/oncall:latest`
- `us-east1-docker.pkg.dev/XY-Corp/oncall/oncall:v1.0.0`
- `us-east1-docker.pkg.dev/XY-Corp/oncall/oncall:main-abc1234`
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:
1. Verify your service account has the correct permissions
2. Check that the `WIF_PROVIDER` secret matches your Workload Identity Provider
3. Ensure the `WIF_SERVICE_ACCOUNT` secret matches your service account email
4. Verify the `GCP_PROJECT_ID` matches your actual project ID
5. Ensure the Workload Identity Federation is properly configured

### Repository Creation Issues

If repository creation fails:
1. Ensure your service account has `Artifact Registry Administrator` role (only needed for auto-creating repositories)
2. Alternatively, manually create the repositories in GCP Console and use only `Artifact Registry Writer` role
3. Check that the region names in your registry URLs are valid
4. Verify the project ID is correct

### Build Issues

If builds fail:
1. Check the Dockerfile syntax
2. Ensure all required files are present in the repository
3. Review the build logs for specific error messages

## Customization

### Adding More Regions

To add more regions, simply add more registry URLs to the `REGISTRIES` environment variable:

```yaml
env:
  REGISTRIES: |
    us-central1-docker.pkg.dev/XY-Corp/oncall/oncall
    us-east1-docker.pkg.dev/XY-Corp/oncall/oncall
    europe-west1-docker.pkg.dev/XY-Corp/oncall/oncall
    asia-southeast1-docker.pkg.dev/XY-Corp/oncall/oncall
```

### Changing Build Context

If you need to build from a different directory, update the `context` parameter in the build step:

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: ./path/to/build/context
    file: ./path/to/Dockerfile
```

### Adding Build Arguments

To pass additional build arguments, add them to the `build-args` section:

```yaml
build-args: |
  BUILD_DATE=${{ fromJSON(steps.meta.outputs.json).labels['org.opencontainers.image.created'] }}
  VCS_REF=${{ github.sha }}
  VERSION=${{ fromJSON(steps.meta.outputs.json).labels['org.opencontainers.image.version'] }}
  CUSTOM_ARG=value
```
