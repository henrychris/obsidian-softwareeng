---
share: "true"
---
# Intro
Docker is a platform for developing, shipping and running apps using containerisation (to place an app in a container). It provides a consistent environment for applications to run, making it easier to develop, deploy, and scale software across different environments. Here are the key concepts:

1. **Containers**: Containers are lightweight, isolated, and portable environments that package an application and its dependencies. They ensure that an application runs consistently on any system.
2. **Images**: Docker images are read-only templates that define the application, its dependencies, and the runtime environment. Images are used to create containers.
3. **Dockerfile**: A Dockerfile is a script that defines the steps to create a Docker image. It specifies the base image, adds application code, and sets up the environment.
4. **Registry**: Docker images are stored in registries like Docker Hub. You can push and pull images from these repositories.
5. **Containerization**: Docker allows you to create, start, stop, move, and delete containers. Each container is an instance of a Docker image.
6. **Orchestration**: Docker can be used in container orchestration platforms like Kubernetes and Docker Swarm to manage and scale containers across multiple hosts.
7. **Isolation**: Containers are isolated from each other and the host system, ensuring that applications do not interfere with each other or with the host.
8. **Portability**: Docker containers can run on any system that supports Docker, whether it's a developer's laptop, a testing environment, or a production server.
9. **Efficiency**: Containers use fewer system resources compared to traditional virtual machines, making them efficient for running multiple applications on a single host.


For a practical application of Docker concepts, especially in a .NET environment with SQL Server, refer to the note on [[06-backend/Using Docker for SQLServer in .NET]].

Related: [[06-backend/Using Docker for SQLServer in .NET]], [How to containerize your ASP.NET Core application and SQL Server with Docker](https://www.twilio.com/blog/containerize-your-aspdotnet-core-application-and-sql-server-with-docker), [Docker for .NET Developers (Part 1)](https://www.stevejgordon.co.uk/docker-dotnet-developers-part-1), [Why isn't my ASP.NET Core app in Docker working? (andrewlock.net)](https://andrewlock.net/why-isnt-my-aspnetcore-app-in-docker-working/)

- [Nuget and Docker](https://blog.devops.dev/consuming-private-nuget-feeds-from-a-dockerfile-in-a-secure-and-devops-friendly-manner-b5c90ea90bba)
- [Build Args in Docker Compose](https://stackoverflow.com/questions/50734271/how-to-define-build-args-in-docker-compose)
- 