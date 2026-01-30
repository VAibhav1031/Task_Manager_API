# Lesson Learned :

# 1. Batch Processing (background concurrent task runnner /worker/)

##  Why Concurrent Worker Error Wasn't Working in the First Go?

### Rebinding and Mutation

These are two things we all get to know, but we still make problems when we use it in modules - things get broken.

---

### The Problem

Let me give you an example:

I was trying to make an **I/O based concurrent threaded worker**, and in that there is one variable (which is the immutable one).

#### File Structure:

__init__.py    # declared all variables I want to use
bucket.py
manager.

#### What Happened:

- In the **bucket module**, I had to use one of the variables `total_request` and I imported that and made an update
- That same variable I had to use in **manager.py** (which is the threaded one) for logging purpose
- **The problem:** I wasn't able to get the updated value that I expected
  - In the bucket module it was updating
  - But I was **REBINDING** there and a new reference was created with the same name for that module level
  - Because of that, I was only able to get whatever value I initialized the variable in the latter module (`__init__.py`)

---

### WHY?

**First thing:** Whenever you import a variable from a module, that is a **copy reference** to that object.

Whenever you do something like:
```python
total_request += 1
```

It is just creating a **new object** and referencing to that one - which means a **new reference and object is created (rebind)**.

Then that object of that module won't help you much.

**YOU'LL see this in IMMUTABLE objects only** - they only show you this type of bug.

---

### SOLUTION

**Use module namespace attribute thing**, because we know modules use to manage the namespace (an object in dictionary format, basically for the variables only - GLOBAL ones).

```python
module_name.attribute = value
```

It is directly using that value and when you update things it fully changes and all. **Rebinding is removed** and things worked.

You will not find this issue anymore.

Then that object of that module won't help you much.

**YOU'LL see this in IMMUTABLE objects only** - they only show you this type of bug.


