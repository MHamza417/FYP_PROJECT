```groovy
pipeline {
    agent any

    stages {

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'Sonar-Server'

                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Build and Deploy Backend') {
            steps {
                sh '''
                docker build -t intellisecops-backend:latest ./backend

                docker stop intellisecops-backend || true
                docker rm intellisecops-backend || true

                docker run -d \
                --name intellisecops-backend \
                -p 5000:5000 \
                intellisecops-backend:latest

                echo "Waiting for backend to start..."
                sleep 10

                echo "Checking backend..."
                curl -f http://127.0.0.1:5000
                '''
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                sh '''
                mkdir -p zap-reports
                chmod 777 zap-reports

                docker run --rm \
                -u root \
                -v "$(pwd)/zap-reports:/zap/wrk" \
                ghcr.io/zaproxy/zaproxy:stable \
                zap-baseline.py \
                -t http://13.63.222.33 \
                -r report.html \
                -J report.json || true

                echo "ZAP scan completed"
                echo "Checking generated reports..."

                ls -lah zap-reports
                '''
            }
        }

        stage('Send Report to Django') {
            steps {
                sh '''
                echo "Sending ZAP report to Django..."

                curl -f -X POST \
                http://127.0.0.1:5000/api/analyze-report/ \
                -H "Content-Type: application/json" \
                --data-binary @zap-reports/report.json

                echo "ZAP report successfully sent to Django"
                '''
            }
        }

        stage('Archive ZAP Reports') {
            steps {
                archiveArtifacts artifacts: 'zap-reports/*', allowEmptyArchive: false
            }
        }
    }
}
```
