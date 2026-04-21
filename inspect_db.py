from database import Session, Base, engine

session = Session()

print("=== DATABASE CONTENTS ===\n")

# Print every table automatically
for table in Base.metadata.sorted_tables:
    print(f"------Table: {table.name.upper()}")
    rows = session.query(table).all()
    
    if not rows:
        print("   (empty)\n")
        continue
    
    for row in rows:
        print("   ", {col.name: getattr(row, col.name) for col in table.columns})
    print("-" * 40)

session.close()
print("✅ Done.")