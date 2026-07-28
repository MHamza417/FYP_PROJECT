pipeline {
    agent any
    stages {
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