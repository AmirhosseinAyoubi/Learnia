// AI-assisted implementation.
// Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
package com.learnia.user.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeIn;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger configuration for the User Service. */
@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "Learnia User Service",
        version = "1.0",
        description = "API for managing user profiles and accounts."
    ),
    security = @SecurityRequirement(name = "X-API-Key")
)
@SecurityScheme(
    name = "X-API-Key",
    type = SecuritySchemeType.APIKEY,
    in = SecuritySchemeIn.HEADER,
    paramName = "X-API-Key",
    description = "API key issued by the Learnia auth-service. Pass it in the X-API-Key header."
)
public class OpenApiConfig {
}
