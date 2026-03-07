pipeline {
    agent any

    environment {
        APP_NAME    = 'aceest-fitness'
        IMAGE_TAG   = "${APP_NAME}:${BUILD_NUMBER}"
        IMAGE_LATEST = "${APP_NAME}:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Pulling latest code from GitHub ==='
                checkout scm
                sh 'echo "Branch: $(git rev-parse --abbrev-ref HEAD)"'
                sh 'echo "Commit: $(git rev-parse HEAD)"'
            }
        }

        stage('Environment Setup') {
            steps {
                echo '=== Setting up Python virtual environment ==='
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '=== Running flake8 linter ==='
                sh '''
                    . venv/bin/activate
                    flake8 app.py test_app.py \
                        --count \
                        --max-line-length=120 \
                        --statistics \
                        --exclude=venv
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo '=== Running pytest unit tests ==='
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v \
                        --tb=short \
                        --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    // Publish test results in Jenkins UI
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "=== Building Docker image: ${IMAGE_TAG} ==="
                sh "docker build -t ${IMAGE_TAG} -t ${IMAGE_LATEST} ."
                sh "docker images ${APP_NAME}"
            }
        }

        stage('Docker Test') {
            steps {
                echo '=== Running tests inside Docker container ==='
                sh """
                    docker run --rm \\
                        -v \$(pwd)/test_app.py:/app/test_app.py \\
                        --entrypoint pytest \\
                        ${IMAGE_LATEST} \\
                        test_app.py -v --tb=short
                """
            }
        }

    }

    post {
        success {
            echo '''
            =============================================
             BUILD SUCCESS - ACEest CI/CD Pipeline
            =============================================
             All stages completed successfully:
              ✅ Checkout
              ✅ Environment Setup
              ✅ Lint
              ✅ Unit Tests
              ✅ Docker Build
              ✅ Docker Test
            =============================================
            '''
        }
        failure {
            echo '''
            =============================================
             BUILD FAILED - ACEest CI/CD Pipeline
            =============================================
             Check the logs above for the failing stage.
            =============================================
            '''
        }
        always {
            // Clean up Docker image after build to save disk space
            sh "docker rmi ${IMAGE_TAG} || true"
            cleanWs()
        }
    }
}