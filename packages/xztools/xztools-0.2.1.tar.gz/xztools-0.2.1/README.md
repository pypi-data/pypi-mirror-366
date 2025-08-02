# xztools

A fun and useful Python library with time utilities and random compliments!

## Installation

```bash
pip install xztools
```

## Features

### 🕐 Time Remaining Function
Get a beautiful countdown report showing how many days are left for:
- **Weekend**: Days until the end of Sunday
- **Month**: Days until the end of current month  
- **Year**: Days until New Year's Eve

### 💝 Random Compliments
Get random compliments to brighten your day!

## Usage

```python
import xztools

# Get time remaining report
print(xztools.time_remaining())

# Get a random compliment
print(xztools.random_compliment())
```

## Example Output

```
⏰ TIME REMAINING REPORT ⏰
========================================

📅 Today: Wednesday, December 20, 2023
========================================

🎉 Weekend Countdown: 4 days until Sunday
📅 Month Countdown: 11 days until end of December
🎊 Year Countdown: 11 days until New Year!

========================================

You're awesome!
```

## Requirements

- Python 3.6 or higher

## License

MIT License

## Contributing

Feel free to contribute by adding more fun utilities to this package! 