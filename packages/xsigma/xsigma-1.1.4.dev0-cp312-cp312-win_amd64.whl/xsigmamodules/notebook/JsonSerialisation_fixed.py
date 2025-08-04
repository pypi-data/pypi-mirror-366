"""
Converted from Jupyter notebook: JsonSerialisation_fixed.ipynb
"""

# %%
# Markdown cell:
# # JSON Serialization in PRETORIAN
# 
# This notebook demonstrates how to serialize and deserialize objects to/from JSON in the PRETORIAN framework.

# %%
from xsigmamodules.Util import (
    datetimeHelper,
    dayCountConvention,
    yearMonthDay,
    calendar,
)
from xsigmamodules.Market import (
    discountCurveFlat,
    anyObject,
    anyId,
    discountCurveId,
    anyContainer,
    discountCurve,
    marketData,
)
from xsigmamodules.util.misc import xsigmaGetDataRoot, xsigmaGetTempDir
import os

# %%
# Markdown cell:
# ## Setup Data Directory
# 
# First, let's set up the data directory where we'll save our JSON files.

# %%
# Get the data root directory
XSIGMA_DATA_ROOT = xsigmaGetDataRoot()
print(f"Data root directory: {XSIGMA_DATA_ROOT}")

# Create a subdirectory for our JSON files
JSON_DIR = os.path.join(XSIGMA_DATA_ROOT, "json_serialization")
os.makedirs(JSON_DIR, exist_ok=True)
print(f"JSON directory: {JSON_DIR}")

# %%
# Markdown cell:
# ## Create and Serialize Objects
# 
# Now let's create some objects and serialize them to JSON.

# %%
# Create a valuation date
valuation_date = yearMonthDay(2020, 1, 21).to_datetime()
print(f"Valuation date: {valuation_date}")

# Create a discount curve
discount_curve = discountCurveFlat(valuation_date, 0.01, dayCountConvention())

# Serialize the discount curve to JSON
discount_curve_path = os.path.join(JSON_DIR, "discount_curve_flat.json")
discount_curve.write_to_json(discount_curve_path, discount_curve)
print(f"Discount curve serialized to: {discount_curve_path}")

# %%
# Markdown cell:
# ## Wrap Objects in anyObject
# 
# The `anyObject` class is a wrapper that can hold any object. This is useful for storing objects in containers.

# %%
# Wrap the discount curve in an anyObject
any_obj = anyObject(discount_curve)

# Serialize the anyObject to JSON
any_obj_path = os.path.join(JSON_DIR, "any_object_discount_curve_flat.json")
any_obj.write_to_json(any_obj_path, any_obj)
print(f"anyObject serialized to: {any_obj_path}")

# %%
# Markdown cell:
# ## Deserialize Objects
# 
# Now let's deserialize the objects from JSON.

# %%
# Deserialize the anyObject from JSON
deserialized_any_obj = anyObject.read_from_json(any_obj_path)
print(f"Deserialized anyObject index: {deserialized_any_obj.index()}")

# Deserialize the discount curve from JSON
deserialized_discount_curve = discountCurveFlat.read_from_json(discount_curve_path)
# The discountCurveFlat class doesn't have a rate() method
# Let's print the object instead
print(f"Deserialized discount curve: {deserialized_discount_curve}")

# %%
# Markdown cell:
# ## Create and Use IDs
# 
# The `anyId` class is a wrapper for IDs that can be used to identify objects in containers.

# %%
# Create a discount curve ID
discount_id = discountCurveId("EUR3M", "EUR")
print("Discount curve ID:")
print(discount_id)

# %%
# Wrap the ID in an anyId
any_id = anyId(discount_id)
print("anyId:")
print(any_id)

# %%
# Markdown cell:
# ## Create and Use Containers
# 
# The `anyContainer` class is a container that can hold objects identified by IDs.

# %%
# Create a container with the discount curve
container = anyContainer([any_id], [any_obj])
print("Container:")
print(container)

# %%
# Markdown cell:
# ## Update the Container
# 
# Now let's add another object to the container.

# %%
# Create another ID and object
another_id = anyId(discountCurveId("EUR6M", "EUR"))
another_obj = anyObject(discount_curve)

# Update the container
container.update([another_id], [another_obj])
print("Updated container:")
print(container)

# %%
# Markdown cell:
# ## Access Objects in the Container
# 
# Now let's access the objects in the container using their IDs.

# %%
# Check if the container contains the ID
print(f"Container contains EUR3M: {container.contains(any_id)}")
print(f"Container contains EUR6M: {container.contains(another_id)}")

# %%
# Since anyContainer doesn't have a 'get' method, we need to use a different approach
# We can check if the container contains the ID
if container.contains(another_id):
    print(f"Container contains the ID: {another_id}")
    print("Container content:")
    print(container)
else:
    print(f"Container does not contain the ID: {another_id}")

# %%
# Markdown cell:
# ## Serialize the Container
# 
# Finally, let's serialize the container to JSON.

# %%
# Serialize the container to JSON
container_path = os.path.join(JSON_DIR, "container.json")
anyContainer.write_to_json(container_path, container)
print(f"Container serialized to: {container_path}")

# Deserialize the container from JSON
deserialized_container = anyContainer.read_from_json(container_path)
print("Deserialized container:")
print(deserialized_container)

# %%
# Markdown cell:
# ## Summary
# 
# In this notebook, we've demonstrated how to:
# 
# 1. Create and serialize objects to JSON
# 2. Deserialize objects from JSON
# 3. Use `anyObject` to wrap objects
# 4. Use `anyId` to identify objects
# 5. Use `anyContainer` to store objects identified by IDs
# 6. Update and access objects in a container
# 7. Serialize and deserialize containers
