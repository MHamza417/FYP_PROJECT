pipeline {
agent any


stages {

    stage('SonarQube Analysis') {
        steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                script {
                    def scannerHome = tool 'Sonar-Server'

                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }
    }

    stage('Build and Deploy Backend') {
        steps {
            sh '''
                echo "Building Docker image..."

                docker build -t intellisecops-backend:latest ./backend

                echo "Stopping old container..."

                docker stop intellisecops-backend || true
                docker rm intellisecops-backend || true

                echo "Starting new backend container..."

                docker run -d \
                    --name intellisecops-backend \
                    -p 5000:5000 \
                    intellisecops-backend:latest

                echo "Waiting for backend..."

                for i in $(seq 1 10); do
                    if curl -sf http://127.0.0.1:5000 > /dev/null; then
                        echo "Backend is up."
                        break
                    fi
                    echo "Backend not ready yet, retrying ($i/10)..."
                    sleep 3
                done

                echo "Checking backend health..."

                curl -f http://127.0.0.1:5000

                echo "Backend deployed successfully!"
            '''
        }
    }

    stage('OWASP ZAP Scan') {
        steps {
            sh '''
                echo "Preparing ZAP reports directory..."

                mkdir -p zap-reports
                chmod 777 zap-reports

                echo "Starting OWASP ZAP scan..."

                docker run --rm \
                    -u root \
                    -v "$(pwd)/zap-reports:/zap/wrk" \
                    ghcr.io/zaproxy/zaproxy:stable \
                    zap-baseline.py \
                    -t http://13.63.222.33 \
                    -r report.html \
                    -J report.json || true

                echo "ZAP scan completed."

                echo "Generated reports:"

                ls -lah zap-reports
            '''
        }
    }

    stage('Send Report to Django') {
        steps {
            sh '''
                echo "Sending ZAP report to Django API..."

                if [ -f zap-reports/report.json ]; then

                    curl -f -X POST \
                        http://127.0.0.1:5000/api/analyze-report/ \
                        -H "Content-Type: application/json" \
                        --data-binary @zap-reports/report.json

                    echo "ZAP report successfully sent to Django!"

                else

                    echo "ERROR: ZAP report.json was not generated!"
                    exit 1

                fi
            '''
        }
    }

    stage('Archive ZAP Reports') {
        steps {
            echo 'Archiving ZAP reports...'

            archiveArtifacts artifacts: 'zap-reports/*',
                allowEmptyArchive: false

            echo 'ZAP reports archived successfully!'
        }
    }
}

post {
    success {
        echo '======================================'
        echo 'PIPELINE COMPLETED SUCCESSFULLY!'
        echo '======================================'
    }

    failure {
        echo '======================================'
        echo 'PIPELINE FAILED!'
        echo 'Check the Jenkins console output.'
        echo '======================================'
    }
}
}