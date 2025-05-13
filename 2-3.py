def contains_duplicate(nums):
    nums.sort()
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1]:
            return True
    return False

print(contains_duplicate([1,3,6,8]))
print(contains_duplicate([1,2,5,3,3,4,6,3,4,7]))
print(contains_duplicate([1,2,3,1]))