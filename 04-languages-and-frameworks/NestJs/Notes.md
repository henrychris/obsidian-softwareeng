# Setup
I created a new project with: `nest new project-name --strict`. The strict flag creates a project with strict Typescript config.

I used `nest g resource [resource-name]` to create a new resource. A resource is an entity we wish to perform CRUD operations on. This command creates a controller, service, entity, dto, test files and module for the resource, in a folder named after said resource.
The module is also added to the `AppModule`.

I prefer to change the main.ts file to use callbacks, instead of await-ing when starting the application. This way, I can log the application URL.

```ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app/app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const PORT = 3000;
  app
    .listen(PORT)
    .then(() => {
      console.log(`App listening on http://localhost:${PORT}`);
    })
    .catch((error) => {
      console.error(error);
      app.close();
    });
}
bootstrap();
```

Modules group controllers and services together. I think it's best to group services and controllers for a module, then register the module in `AppModule`. This way, we only register a single Module in `main.ts`. Seems clean and orderly to me.

Use `nest g service [service-name]` and `nest g module [module-name]` to create a service and module respectively.

To authorise requests, we will use [guards](https://docs.nestjs.com/guards).

# Configuration
Install two packages: `@nestjs/config` and `joi`.
In `AppModule`, set up the `ConfigModule` from `@nestjs/config` and register it as a global module. It's best to add validation with `joi` here, so the application fails to start if config is missing.

```ts
@Module({
  imports: [
    UsersModule,
    ExpensesModule,
    ConfigModule.forRoot({
      isGlobal: true,
      validationSchema: Joi.object({
        NODE_ENV: Joi.string()
          .valid('development', 'production', 'test', 'provision')
          .default('development'),
        PORT: Joi.number().required(),
        DB_URL: Joi.string().uri().required(),
        DATABASE_PASSWORD: Joi.string().required(),
      }),
      validationOptions: {
        noDefaults: true,
        abortEarly: false,
      },
    }),
  ],
  controllers: [AppController],
  providers: [AppService],
})
```

In a config folder, add interfaces representing the values in configuration:
```ts
export default interface AppConfig {
  PORT: number;
}
```

In a service, inject `ConfigService` from `@nestjs/config`, with the interface of the needed settings
```ts
constructor(
    private configService: ConfigService<AppConfig>,
    private dbConfig: ConfigService<DatabaseConfig>,
  ) {}
```

Access the value
```ts
// when infer == true, it infers the type of the config as specified in 
// the interface
let port = this.configService.get('PORT', { infer: true });
```

In `main.ts`, you can access configuration from the `app` variable:
```ts
const configService = app.get(ConfigService);
const PORT: number = configService.getOrThrow('PORT');
```

Reference: [NestJs Configuration](https://docs.nestjs.com/techniques/configuration)
# Database & Migrations
I currently prefer to use TypeORM.
First, I added properties to my database config interface.
```ts
export default interface DatabaseConfig {
  DATABASE_NAME: string;
  DATABASE_HOST: string;
  DATABASE_PORT: string;
  DATABASE_USERNAME: string;
  DATABASE_PASSWORD: string;
}
```

Then installed the dependencies:
```bash
npm i -g typeorm

npm install --save @nestjs/typeorm pg

npm install ts-node --save-dev
```

In `AppModule`, configure TypeOrm:
```ts
TypeOrmModule.forRootAsync({
      useFactory: (configService: ConfigService<DatabaseConfig>) => ({
        type: 'postgres',
        host: configService.getOrThrow('DATABASE_HOST'),
        port: configService.getOrThrow('DATABASE_PORT'),
        username: configService.getOrThrow('DATABASE_USERNAME'),
        password: configService.getOrThrow('DATABASE_PASSWORD'),
        database: configService.getOrThrow('DATABASE_NAME'),
        autoLoadEntities: true,
        migrations: [__dirname + 'data/migrations/**/*{.ts,.js}'],
        cli: {
          migrationsDir: __dirname + 'data/migrations/',
        },
      }),
      inject: [ConfigService],
    }),
```

Note that we set `autoLoadEntities` to true. We will revisit this below when registering TypeOrm in modules.
in `src/data`, create a `dataSource.ts` file. The migrations will be run against this file.
```ts
import * as dotenv from 'dotenv';
dotenv.config();
import { DataSource } from 'typeorm';

export default new DataSource({
  type: 'postgres',
  host: process.env.DATABASE_HOST,
  port: parseInt(process.env.DATABASE_PORT!),
  username: process.env.DATABASE_USERNAME,
  password: process.env.DATABASE_PASSWORD,
  database: process.env.DATABASE_NAME,
  synchronize: false,
  dropSchema: false,
  logging: false,
  logger: 'simple-console',
  entities: ['src/**/*.entity{.ts,.js}'], // change src to dist if it doesn't work 
  migrations: ['src/data/migrations/**/*{.ts,.js}'],
});
```

Create an entity. Make sure the class is exported:
```ts
@Entity({ name: 'Expenses' })
export class Expense {
  @PrimaryGeneratedColumn('uuid')
  id: number;

  @Column()
  amount: number;

  @Column({ length: 3 })
  currency: string;

  @Column()
  passwordHash: string;

  @ManyToOne(() => User, (user) => user.expenses)
  user: User;
}
```

In the module, make sure to import TypeOrm and specify the entities you will use in that module. Note that when `autoLoadEntities` is true, entities must be registered to be loaded.
```ts
@Module({
  imports: [TypeOrmModule.forFeature([Expense, User, Other])],
  exports: [TypeOrmModule], // re-export this
  controllers: [ExpensesController],
  providers: [ExpensesService],
})
```

If you want to use the repository outside of the module which imports `TypeOrmModule.forFeature`, you'll need to re-export TypeOrm, like above.

Add these scripts to `package.json`
```json
{
	"typeorm": "typeorm-ts-node-commonjs",
	"migration:generate": "typeorm-ts-node-commonjs migration:generate ./src/data/migrations/schema-update -d ./src/data/dataSource.ts -p",
	"migration:run": "typeorm-ts-node-commonjs migration:run -d  ./src/data/dataSource.ts",
	"migration:revert": "typeorm-ts-node-commonjs migration:revert -d ./src/data/dataSource.ts",
    "schema:sync": "typeorm-ts-node-commonjs schema:sync -d ./src/data/dataSource.ts"
}
```

Use them to manage and apply migrations.

Finally, inject a repository in a service like so:
```ts
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}
```

**Note:** Always use relative paths when importing files.

Reference: [TypeOrm Migrations on Medium](https://dev.to/andymwamengo/how-to-create-and-generate-migrations-in-typeorm-03-with-nestjs-9-4g55), [NestJs Database](https://docs.nestjs.com/techniques/database), [TypeOrm](https://typeorm.io/)
# Request Validation
This is fairly simple. Install these packages:
```bash
npm i --save class-validator class-transformer
```

Register the validation pipe in `main.ts`
```ts
const app = await NestFactory.create(AppModule);
  app.use(logger('dev'));
  app.useGlobalPipes(
    new ValidationPipe({
      errorHttpStatusCode: HttpStatus.UNPROCESSABLE_ENTITY,
    }),
  );
```

Decorate dto classes that require input validation. For example:
```ts
import { IsEmail, IsNotEmpty, MinLength } from 'class-validator';

export class LoginRequest {
  @IsNotEmpty()
  @IsEmail()
  email: string;

  @IsNotEmpty()
  @MinLength(6)
  password: string;
}
```

## Transforms
NestJS will try converting the input data to a JSON object, based on the type info in the dto. By default, all data received is a 'string', and are converted to their types.

To enable this, set `transform = true` in the validation pipe configuration.
```ts
app.useGlobalPipes(
    new ValidationPipe({
      errorHttpStatusCode: HttpStatus.UNPROCESSABLE_ENTITY,
      transform: true,
      enableDebugMessages: true,
    }),
  );
```

You can enable implicit conversion too, but that *could* lead to weird bugs like converting `true` to `1`. In theory sha.
```ts
app.useGlobalPipes(
    new ValidationPipe({
      errorHttpStatusCode: HttpStatus.UNPROCESSABLE_ENTITY,
      transform: true,
      enableDebugMessages: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );
```

You can go granular and apply direct transformations by decorating the property.
```ts
  @Type(() => Number) // option 1
  @Transform(({ value }) => +value) // option 2
  page: number;
```

Reference: [Nest Js Validation](https://docs.nestjs.com/techniques/validation), [Github Issue]([Validation pipe primitive transformation not working · Issue #5253 · nestjs/nest](https://github.com/nestjs/nest/issues/5253)), [Nest Js Transforms](https://docs.nestjs.com/techniques/validation#transform-payload-objects).

# Auth Guard - JWT Validation
This works in tandem with the auth and login endpoints because they issue the access token to the user. First create a class to represent the user data in the JWT.
```ts
export class JwtPayload {
  constructor(userId: string) {
	this.sub = userId;
  }
  sub: string;
}
```

The auth guard, borrowed from [here](https://docs.nestjs.com/security/authentication#implementing-the-authentication-guard), validates the JWT. If invalid, it returns a 401, else it adds the user to the current request.
```ts
@Injectable()
export class AuthGuard implements CanActivate {
  constructor(
    private jwtService: JwtService,
    private configService: ConfigService<JwtConfig>,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const token = this.extractTokenFromHeader(request);
    if (!token) {
      throw new UnauthorizedException();
    }
    try {
      const payload: JwtPayload = await this.jwtService.verifyAsync(token, {
        secret: this.configService.getOrThrow('JWT_SECRET'),
      });

      // 💡 We're assigning the payload to the request object here
      // so that we can access it in our route handlers
      request['user'] = payload;
    } catch {
      throw new UnauthorizedException();
    }
    return true;
  }

  private extractTokenFromHeader(request: Request): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}
```

Note the config & nest JWT services are injected here. 

You can use it on a controller like so:
```ts
@UseGuards(AuthGuard)
  @Get('profile')
  getProfile(@CurrentUser() user: JwtPayload) {
    return user;
  }
```

or implement it by default by adding it in `providers` in any module:
```ts
providers: [
  {
    provide: APP_GUARD,
    useClass: AuthGuard,
  },
],
```

I also added a `@CurrentUser` decorator to get the user info from the request, instead of adding `@Request` to controllers. As long as the route is authorised, we can use `@CurrentUser`.
```ts
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const CurrentUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return request.user;
  },
);
```

To use the `AuthGuard` in other modules **without** registering it globally as above, you'll need to do the following in `AuthModule`:
- register `AuthGuard` as a provider
- export `AuthGuard`
- export `JwtModule`

Finally, import `AuthModule` in modules that require `AuthGuard`.

Reference: [NestJs Authentication](https://docs.nestjs.com/security/authentication)

# Caching
This is fairly straightforward. Refer to this: [Caching NestJs](https://docs.nestjs.com/techniques/caching). You can customise it to add a different store, such as Redis. 
You can also reference this: [Medium](https://medium.com/@citi_zen/implementing-caching-in-nestjs-quick-guide-2cfe50dd241d). It contains the same info as the NestJs docs.
# Rate Limiting
[NestJs Throttler](https://github.com/jmcdo29/nest-lab/tree/main/packages/throttler-storage-redis)

This is also straightforward. See this: [Rate Limiting NestJs](https://docs.nestjs.com/security/rate-limiting). After configuring the module:
```ts
ThrottlerModule.forRoot([
      {
        ttl: 60000,
        limit: 10,
      },
    ]),
```

These options are bound across the application. You can bind the *ThrottlerGuard* globally by adding this provider to any module:
```ts
{
  provide: APP_GUARD,
  useClass: ThrottlerGuard
}
```

or by decorating the controller you wish to throttle requests on:
```ts
  @UseGuards(ThrottlerGuard)
  @Get()
  async findAll(
    @CurrentUser() jwtUser: JwtPayload,
    @Query() filterDto: ExpenseFilterDto,
  ) {
    return await this.expensesService.findAllAsync(jwtUser, filterDto);
  }
```

# Swagger / OpenAPI
This is also simple. See [NestJs Swagger](https://docs.nestjs.com/openapi/introduction).

# Standardising Responses
This is a two-part solution.
An interceptor:
```ts
@Injectable()
export class SuccessResponseInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map((data) => ({
        success: true,
        message: 'Success',
        data,
      })),
    );
  }
}
```

An error filter:
```ts
@Catch()
export class ErrorResponseFilter implements ExceptionFilter {
  catch(exception: any, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    const errorResponse = {
      success: false,
      message: exception.message || 'An unexpected error occurred.',
      errors: exception.response?.message
        ? Array.isArray(exception.response.message)
          ? exception.response.message.map((msg: any) => ({ message: msg }))
          : [{ message: exception.response.message }]
        : [{ message: 'An unexpected error occurred.' }],
    };

    // todo: add more steps for various status codes.
    if (status === HttpStatus.UNPROCESSABLE_ENTITY) {
      errorResponse.message = 'One or more validation errors';
    }

    response.status(status).json(errorResponse);
  }
}
```

Both are registered in `main.ts`:
```ts
	app.useGlobalFilters(new ErrorResponseFilter());
	app.useGlobalInterceptors(new SuccessResponseInterceptor());
```

This *works*. But all responses are affected, even the index endpoint that ought to return only a string. Also, this won't display the expected response bodies on Swagger / OpenAPI.
There is room for **improvement** here. 