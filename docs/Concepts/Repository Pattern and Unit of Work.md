---
share: "true"
---
## Repository Pattern

The Repository Pattern is a structural design pattern used to abstract and centralize data access in an application. It separates the data access logic from the rest of the application, providing a more organized and maintainable way to work with data. In this context, we are implementing a generic repository pattern.

### Interfaces

1. `IBaseRepository<TEntity>`: This is a generic interface that defines common data access methods like GetById, GetAll, Find, Add, Remove, Exists, and Update for a specific entity type (`TEntity`).
```
public interface IBaseRepository<TEntity> where TEntity : class  
{  
    Task<TEntity?> GetByIdAsync(string id);  
    Task<IEnumerable<TEntity>> GetAllAsync();
    // other methods
}
```

2. `IEventRepository`: An interface that inherits from `IBaseRepository<Event>`, specializing in data access methods for the `Event` entity.    

### Base Repository

The `BaseRepository<TEntity>` class implements the `IBaseRepository<TEntity>` interface and provides common data access methods. It uses the Entity Framework Core's `DbContext` to interact with the database.

```
public class BaseRepository<TEntity> : IBaseRepository<TEntity> where TEntity : class  
{  
    protected readonly DbContext Context;  
  
    protected BaseRepository(DbContext context)  
    {        Context = context;  
    }  
    public async Task<TEntity?> GetByIdAsync(string id)  
    {        return await Context.Set<TEntity>().FindAsync(id);  
    }  
    public async Task<IEnumerable<TEntity>> GetAllAsync()  
    {        return await Context.Set<TEntity>().ToListAsync();  
    }

	// other methods
}
```

### EventRepository

The `EventRepository` class inherits from `BaseRepository<Event>`, providing specialized data access methods for the `Event` entity. It uses the `EventDbContext` as the data context.
We have to cast the context to our EventDbContext to access the Event DbSet.

```

public class EventRepository : BaseRepository<Event>, IEventRepository  
{  
    public EventRepository(DbContext context) : base(context)  
    {    }  
    private EventDbContext EventDbContext => Context as EventDbContext ??  
                                             throw new InvalidCastException("Event DB Context not passed from unit of work.");

}
```

## Unit of Work

The Unit of Work pattern is a behavioral design pattern used to manage database transactions and coordinate multiple repositories. It ensures that changes to the database are consistent and that transactions are properly managed.
### Interfaces

1. `IUnitOfWork`: An interface that defines the unit of work. It provides access to repositories and methods to manage transactions.
```
public interface IUnitOfWork : IDisposable  
{  
    IEventRepository Events { get; }  
    void BeginTransaction();  
    Task CompleteAsync();  
    void Commit();  
    void Rollback();  
}
```
### UnitOfWork

The `UnitOfWork` class implements the `IUnitOfWork` interface. It serves as a central point for coordinating data access. The key features are:

- **Repository Access**: The `IEventRepository` is accessible via the `Events` property, providing a way to access the data in a structured manner.
- **Transaction Management**: It offers methods to begin, commit, and rollback transactions. Transactions are started using the `BeginTransaction` method, and they can be committed or rolled back as needed. The `CompleteAsync` method is used to finalize changes and commit the transaction.
- **Data Context**: The `UnitOfWork` holds a reference to the `EventDbContext`, which is used by the repositories for data access.

```
public class UnitOfWork : IUnitOfWork  
{  
    private readonly EventDbContext _context;  
    private IDbContextTransaction? _transaction;  
  
    public UnitOfWork(EventDbContext context)  
    {        _context = context;  
        Events ??= new EventRepository(_context);  
    }  
    public IEventRepository Events { get; }  
  
    public void BeginTransaction()  
    {        _transaction = _context.Database.BeginTransaction();  
    }  
    public void Commit()  
    {        if (_transaction == null)  
        {            return;  
        }  
        try  
        {  
            _context.SaveChanges();  
            _transaction.Commit();  
        }        catch  
        {  
            Rollback();  
            throw;  
        }        finally  
        {  
            _transaction.Dispose();  
            _transaction = null;  
        }    }  
    public async Task CompleteAsync()  
    {        if (_transaction != null)  
        {            Commit();  
        }        else  
        {  
            await _context.SaveChangesAsync();  
        }    }  
    public void Rollback()  
    {        if (_transaction == null)  
        {            return;  
        }  
        _transaction.Rollback();  
        _transaction.Dispose();  
        _transaction = null;  
    }  
    public void Dispose()  
    {        _context.Dispose();  
    }
}
```

## Usage

The Repository Pattern and Unit of Work are essential components of a modular and organized data access layer. They abstract the database operations, improve code reusability, and make data access more manageable.

In your application, you can use the `IUnitOfWork` and specialized repositories, like `IEventRepository`, to interact with the database while keeping your code clean, maintainable, and free from direct database concerns.