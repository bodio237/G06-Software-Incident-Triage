pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        IMAGE_NAME = 'g06-software-incident-triage'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m pip install -r requirements-dev.txt
                    python3 -m pip install --no-deps -e .
                '''
            }
        }

        stage('Automated tests') {
            steps {
                sh '''
                    mkdir -p reports
                    python3 -m pytest --junitxml=reports/pytest.xml
                '''
            }
        }

        stage('Terraform validate') {
            steps {
                sh '''
                    cd infra
                    terraform init -backend=false -input=false
                    terraform validate
                '''
            }
        }

        stage('Prepare immutable image tag') {
            steps {
                script {
                    def commit = sh(
                        script: 'git rev-parse --short=12 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_REF = "${env.IMAGE_NAME}:g06-${env.BUILD_NUMBER}-${commit}"

                    writeFile(
                        file: 'image-tag.txt',
                        text: "${env.IMAGE_REF}\n"
                    )

                    echo "Image tag: ${env.IMAGE_REF}"
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    docker build -t "${IMAGE_REF}" .
                    docker image inspect "${IMAGE_REF}" > /dev/null
                '''
            }
        }

        stage('Container smoke test') {
            steps {
                sh '''
                    python3 scripts/container_smoke.py "${IMAGE_REF}"
                '''
            }
        }
    }

    post {
        always {
            junit(
                testResults: 'reports/pytest.xml',
                allowEmptyResults: true
            )

            archiveArtifacts(
                artifacts: 'reports/**,image-tag.txt',
                allowEmptyArchive: true
            )
        }

        success {
            echo 'CI pipeline completed successfully.'
        }

        failure {
            echo 'CI pipeline failed. Docker image build/smoke stages are skipped after a failed stage.'
        }
    }
}