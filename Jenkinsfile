pipeline {
    agent any
    stages {
        stage('SonarQube Analysis') {
            steps {
                // Aapka pehle se chalne wala SonarQube step yahan hoga
                script {
                    def scannerHome = tool 'Sonar-Server';
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }
        
        stage('OWASP ZAP Scan') {
            steps {
                sh '''
                mkdir -p zap-reports

                docker run --rm \
                -v $(pwd)/zap-reports:/zap/wrk \
                ghcr.io/zaproxy/zaproxy:stable \
                zap-baseline.py \
                -t http://13.63.222.33 \
                -r report.html \
                -J report.json
                '''
            }
        }
    }
}