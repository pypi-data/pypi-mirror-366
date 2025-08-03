/**
 * Environment Variables Service
 * Fetches environment variables from the backend REST endpoint
 */

export interface IEnvironmentVariables {
    GCP_CLIENT_ID?: string;
    GCP_PROJECT_ID?: string;
    BONNIE_URL?: string;
    ESCOBAR_THEME?: string;
}

export interface IEnvironmentResponse {
    success: boolean;
    variables: IEnvironmentVariables;
    timestamp: string;
    found_count: number;
    total_checked: number;
    error?: string;
}

export class EnvironmentService {
    private cache: IEnvironmentVariables | null = null;
    private cacheTimestamp: number = 0;
    private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

    /**
     * Get the base URL for API requests, handling both JupyterHub and standalone environments
     */
    private getBaseUrl(): string {
        const currentPath = window.location.pathname;

        // Check if we're in JupyterHub (URL contains /user/username/)
        if (currentPath.includes('/user/')) {
            const match = currentPath.match(/^(\/user\/[^\/]+)/);
            return match ? match[1] : '';
        }

        // Standalone JupyterLab
        return '';
    }

    /**
     * Fetch environment variables from the backend REST endpoint
     */
    async fetchEnvironmentVariables(): Promise<IEnvironmentVariables> {
        console.log('🌍 ENV-SERVICE: Fetching environment variables...');

        // Check cache first
        const now = Date.now();
        if (this.cache && (now - this.cacheTimestamp) < this.CACHE_DURATION) {
            console.log('🌍 ENV-SERVICE: Using cached environment variables');
            return { ...this.cache };
        }

        const baseUrl = this.getBaseUrl();
        const endpoint = `${baseUrl}/api/escobar/environment-variables`;

        console.log('🌍 ENV-SERVICE: Requesting from endpoint:', endpoint);

        try {
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin' // Include cookies for authentication
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data: IEnvironmentResponse = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Unknown error from environment variables endpoint');
            }

            console.log('🌍 ENV-SERVICE: Successfully fetched environment variables');
            console.log('🌍 ENV-SERVICE: Found', data.found_count, 'out of', data.total_checked, 'variables');

            // Log found variables (values will be masked by backend)
            Object.entries(data.variables).forEach(([key, value]) => {
                if (value) {
                    const maskedValue = value.length > 15 ? `${value.substring(0, 10)}...${value.substring(value.length - 5)}` : value;
                    console.log(`🌍 ENV-SERVICE: ${key}: ${maskedValue}`);
                }
            });

            // Update cache
            this.cache = { ...data.variables };
            this.cacheTimestamp = now;

            return { ...data.variables };

        } catch (error) {
            console.warn('🌍 ENV-SERVICE: Failed to fetch environment variables:', error);

            // Return empty object on error, don't throw
            // This allows the application to continue working even if the endpoint fails
            return {};
        }
    }

    /**
     * Get a specific environment variable
     */
    async getEnvironmentVariable(name: keyof IEnvironmentVariables): Promise<string | undefined> {
        const variables = await this.fetchEnvironmentVariables();
        return variables[name];
    }

    /**
     * Get Google Client ID specifically
     */
    async getGoogleClientId(): Promise<string | undefined> {
        return await this.getEnvironmentVariable('GCP_CLIENT_ID');
    }

    /**
     * Clear the cache (useful for testing or forcing refresh)
     */
    clearCache(): void {
        this.cache = null;
        this.cacheTimestamp = 0;
        console.log('🌍 ENV-SERVICE: Cache cleared');
    }

    /**
     * Check if a variable is available in cache without making a network request
     */
    getCachedVariable(name: keyof IEnvironmentVariables): string | undefined {
        if (!this.cache) {
            return undefined;
        }
        return this.cache[name];
    }
}

// Export a singleton instance
export const environmentService = new EnvironmentService();
