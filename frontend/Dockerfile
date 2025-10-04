# Use an official Node.js runtime as a parent image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker cache
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of your frontend source code
COPY . .

# The Vite development server runs on port 5173 by default
EXPOSE 5173

# Command to run the development server
# The "--host" flag is crucial to expose the server outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]