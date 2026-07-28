pipeline {
    agent any
    stages {
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'Sonar-Server';
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
                docker run -d --name intellisecops-backend -p 5000:5000 intellisecops-backend:latest
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
                -v $(pwd)/zap-reports:/zap/wrk \
                ghcr.io/zaproxy/zaproxy:stable \
                zap-baseline.py \
                -t http://13.63.222.33 \
                -r report.html \
                -J report.json
                '''
            }
        }

        stage('Send Report to Django') {
            steps {
                script {
                    sh '''
                    curl -X POST http://172.17.0.1:5000/api/analyze-report/ \
                    -H "Content-Type: application/json" \
                    -d @zap-reports/report.json
                    '''
                }
            }
        }
    }
}