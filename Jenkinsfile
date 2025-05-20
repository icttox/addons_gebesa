pipeline {
	agent any
	stages {
		stage('Prepare') {
			steps {
				withCredentials([usernamePassword(credentialsId: '537583b1-1ac5-4e43-bc06-a2d93e392a02', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
					sshPublisher (
						continueOnError: false, failOnError: true,
						publishers: [
							sshPublisherDesc(
								configName: "docker-host",
								verbose: true,
								transfers: [
									sshTransfer(execCommand: """
										cd /home/dockeradmin/odoo-11-ee;
										rm -r addons-grupo-salmon/;
										git clone -b 12.0-samuel http://username:$USERNAME@192.99.14.85:81/gebesa/addons-grupo-salmon;
										cd addons-grupo-salmon;
										git checkout borrar3 && git checkout dev;
										git merge --no-ff borrar3;
									"""),
								]
							)
						]
					)
				}
			}
		}
		stage ('TestPep8') {
			steps {
				sshPublisher (
					continueOnError: false, failOnError: true,
					publishers: [
							sshPublisherDesc(
								configName: "docker-host",
								verbose: true,
								transfers: [
									sshTransfer(execCommand: """
										cd /home/dockeradmin/odoo-11-ee/addons-grupo-salmon;
										/home/dockeradmin/.local/bin/pycodestyle --ignore=E501 .
									"""),
								]
							)
						]
				)
			}
		}
		stage ('DockerOdoo') {
			steps {
				sshPublisher(
					continueOnError: false, failOnError: true,
					publishers: [
						sshPublisherDesc(
							configName: "docker-host",
							verbose: true,
							transfers: [
								sshTransfer(execCommand: """
									docker rm -f odoo12-container-test;
									docker run -P --restart=always --name odoo12-container-test --link db:db -v /home/dockeradmin/odoo-11-ee:/opt/odoo -p 0.0.0.0:8012:8069 -p 0.0.0.0:8022:8072 -d zettox/doceroll:210720;
								"""),
							]
						)
					]
				)
			}
		}
		stage ('DockerOdooTest') {
			steps {
				sshPublisher(
					continueOnError: false, failOnError: true,
					publishers: [
						sshPublisherDesc(
							configName: "docker-host",
							verbose: true,
							transfers: [
								sshTransfer(execCommand: """
									docker exec -i odoo12-container-test bash -c "/opt/odoo/12.0/odoo-bin --log-level=debug --db_host=db --db_port=5432 --db_user=odoo -c /opt/odoo/conf/odoo.conf -i hr_employee_days_tolerance -d demo --test-enable --stop-after-init";
									retVal=\$?
									docker rm -f odoo12-container-test;
									if [\retVal != 0 ] ; then exit 1; fi
								"""),
							]
						)
					]
				)
			}
		}
	}
	post {
        always {
            emailext subject: "Jenkins Build ${currentBuild.currentResult}: Job \"${env.JOB_NAME}\"",
                body: "${currentBuild.currentResult}: Job \"${env.JOB_NAME}\" build ${env.BUILD_NUMBER}.\nMore info at: ${env.BUILD_URL}",
                recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']]
        }
    }
}
