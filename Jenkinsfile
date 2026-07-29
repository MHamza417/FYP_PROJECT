pipeline {
    agent any

    environment {
        GEMINI_API_KEY       = credentials('GEMINI_API_KEY')
        SLACK_WEBHOOK_URL    = credentials('SLACK_WEBHOOK_URL')
        GMAIL_USER           = credentials('GMAIL_USER')
        GMAIL_APP_PASSWORD   = credentials('GMAIL_APP_PASSWORD')
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        EC2_HOST             = credentials('EC2_HOST')
        EC2_SSH_KEY          = credentials('EC2_SSH_KEY')
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
                    pip install -r requirements.txt
                    pip install sqlmap
                '''
            }
        }

        stage('Start ZAP daemon') {
            steps {
                sh '''
                    docker run -d --name zap-daemon -u zap -p 8080:8080 zaproxy/zap-stable \
                        zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true
                    sleep 15
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -f docker/Dockerfile -t intellisecops:latest .'
            }
        }

        stage('Run security scan pipeline') {
            steps {
                sh 'python3 main.py'
            }
        }

        stage('Archive scan report') {
            steps {
                archiveArtifacts artifacts: 'scan_report.json', allowEmptyArchive: true
            }
        }

        stage('Deployment gate') {
            steps {
                script {
                    def report = readJSON file: 'scan_report.json'
                    if (report.deployment_blocked) {
                        error("Deployment blocked: ${report.gate_reason}")
                    } else {
                        echo "Gate passed: ${report.gate_reason}"
                    }
                }
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                sh '''
                    echo "$EC2_SSH_KEY" > key.pem
                    chmod 600 key.pem
                    docker save intellisecops:latest | gzip > image.tar.gz
                    scp -i key.pem -o StrictHostKeyChecking=no image.tar.gz ec2-user@$EC2_HOST:/tmp/
                    ssh -i key.pem -o StrictHostKeyChecking=no ec2-user@$EC2_HOST \
                        "docker load < /tmp/image.tar.gz && docker stop intellisecops || true && docker rm intellisecops || true && docker run -d --name intellisecops intellisecops:latest"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker stop zap-daemon || true'
            sh 'docker rm zap-daemon || true'
        }
        failure {
            echo 'Pipeline failed — check the deployment gate stage or scan logs above.'
        }
    }
}