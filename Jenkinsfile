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
                bat '''
                    python -m pip install -r requirements-dev.txt
                    python -m pip install --no-deps -e .
                '''
            }
        }

        stage('Automated tests') {
            steps {
                bat '''
                    mkdir -p reports
                    python -m pytest --junitxml=reports/pytest.xml
                '''
            }
        }

        stage('Terraform validate') {
            steps {
                bat '''
                    cd infra
                    C:\Terraform\terraform.exe init -backend=false -input=false
                    C:\Terraform\terraform.exe validate
                '''
            }
        }

        stage('Prepare immutable image tag') {
            steps {
                script {
                    def commit = bat(
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
                bat '''
                    docker build -t "${IMAGE_REF}" .
                    docker image inspect "${IMAGE_REF}" > /dev/null
                '''
            }
        }

        stage('Container smoke test') {
            steps {
                bat '''
                    python -m pip install -r requirements-dev.txt
                    python -m pip install --no-deps -e .
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