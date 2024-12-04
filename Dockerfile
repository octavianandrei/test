# Stage 1: Build stage with GCC and hardened flags for amd64/arm64 using Alpine
FROM python:3.9-alpine as builder

# Update package index and install build tools (GCC, musl-dev), Python development headers, Git, and curl
RUN apk update && apk add --no-cache gcc musl-dev python3-dev git curl

# Upgrade pip in the builder stage
RUN pip install --upgrade pip --root-user-action=ignore

WORKDIR /build

# Copy the whole project to the build stage
COPY . /build/

# Install the package (wheel) using pip with hardened compiler flags
RUN CFLAGS="-fstack-protector-strong -fstack-clash-protection -D_FORTIFY_SOURCE=2" pip install . --root-user-action=ignore

# Clean up build tools after installing the package to minimize the image size
RUN apk del gcc musl-dev python3-dev

# Stage 2: Final minimal image without source code
FROM python:3.9-alpine

WORKDIR /app

# Install curl, git, and upgrade pip in the final minimal image stage
RUN apk update && apk add --no-cache curl git && pip install --upgrade pip --root-user-action=ignore

# Create the non-root user before setting permissions, using /bin/false as the shell
RUN addgroup -g 1001 nonroot && adduser -u 1001 -G nonroot -s /bin/false -D nonroot

# Set ownership and permissions for the entire /app directory for the nonroot user
RUN chown -R nonroot:nonroot /app && chmod -R 770 /app

# Remove shell utilities to prevent any user from executing /sh or /bash after user creation
RUN rm /bin/sh

# Copy only the installed Python packages from the builder stage to the final image
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the configuration file from the build context into the container
# COPY src/tc2gl/translate/completion_weight.config /app/src/tc2gl/translate/
# COPY src/tc2gl/translate/step_template_mapping.json /app/src/tc2gl/translate/
# 
# Ensure /usr/local/bin is in PATH
ENV PATH="/usr/local/bin:${PATH}"

# Switch to non-root user for security reasons
USER nonroot

# Set ENTRYPOINT to always use tc2gl as the command
ENTRYPOINT ["tc2gl"]
