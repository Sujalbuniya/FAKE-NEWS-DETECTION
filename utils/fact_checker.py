import re
import datetime

class FactChecker:
    def __init__(self):
        self.common_facts = {
            '2+2': '4',
            'capital of france': 'paris',
            'capital of germany': 'berlin', 
            'largest planet': 'jupiter',
        }
        
        # Current date information
        self.current_date = datetime.datetime.now()
        self.days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        self.current_day = self.days_of_week[self.current_date.weekday()]
        self.current_year = str(self.current_date.year)
        self.current_month = self.current_date.strftime('%B').lower()
        self.current_day_number = str(self.current_date.day)
        
        # Month names and numbers
        self.months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        self.month_names = list(self.months.keys())
    
    def check_date_claims(self, text):
        """Check date-related claims"""
        text_lower = text.lower()
        
        # Check day of week claims
        for day in self.days_of_week:
            if any(phrase in text_lower for phrase in [f"today is {day}", f"it is {day}", f"this day is {day}"]):
                if day != self.current_day:
                    return {
                        'claim': f"Today is {day.title()}",
                        'actual': f"Today is {self.current_day.title()}",
                        'is_correct': False
                    }
        
        # Check specific date patterns like "28th september" or "september 28th"
        date_patterns = [
            r'(\d{1,2})(?:st|nd|rd|th)?\s+(' + '|'.join(self.month_names) + ')',
            r'(' + '|'.join(self.month_names) + r')\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'today is (\d{1,2})(?:st|nd|rd|th)?\s*$',
            r'date is (\d{1,2})(?:st|nd|rd|th)?\s*$',
            r'it is (\d{1,2})(?:st|nd|rd|th)?\s+of\s+(' + '|'.join(self.month_names) + ')'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) == 2:  # Day and month
                    day_num, month_name = match
                    # Clean day number (remove 'st', 'nd', 'rd', 'th')
                    day_num = re.sub(r'(st|nd|rd|th)', '', day_num)
                    
                    month_num = self.months.get(month_name.lower())
                    
                    if month_num == self.current_date.month:
                        if day_num != self.current_day_number:
                            return {
                                'claim': f"Date is {day_num} {month_name.title()}",
                                'actual': f"Date is {self.current_day_number} {self.current_date.strftime('%B')}",
                                'is_correct': False
                            }
                    else:
                        # Wrong month
                        return {
                            'claim': f"Date is {day_num} {month_name.title()}",
                            'actual': f"Current month is {self.current_date.strftime('%B')}",
                            'is_correct': False
                        }
                
                elif len(match) == 1:  # Just day number
                    day_num = match[0]
                    # Clean day number
                    day_num = re.sub(r'(st|nd|rd|th)', '', day_num)
                    
                    if day_num != self.current_day_number:
                        return {
                            'claim': f"Today is {day_num}",
                            'actual': f"Today is {self.current_day_number}",
                            'is_correct': False
                        }
        
        # Check if text contains month name but wrong month
        for month_name in self.month_names:
            if month_name in text_lower:
                month_num = self.months[month_name]
                if month_num != self.current_date.month:
                    return {
                        'claim': f"Month is {month_name.title()}",
                        'actual': f"Current month is {self.current_date.strftime('%B')}",
                        'is_correct': False
                    }
        
        return None
    
    # ... keep the rest of the methods the same (check_math_claim, check_common_facts, check_facts) ...

    def check_math_claim(self, text):
        """Check for simple mathematical claims"""
        math_patterns = [
            r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)',
            r'(\d+)\s*-\s*(\d+)\s*=\s*(\d+)', 
        ]
        
        for pattern in math_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                a, b, claimed = map(int, match)
                
                if '+' in pattern:
                    actual = a + b
                    operation = '+'
                else:
                    actual = a - b
                    operation = '-'
                
                if claimed != actual:
                    return {
                        'claim': f"{a} {operation} {b} = {claimed}",
                        'actual': f"{a} {operation} {b} = {actual}",
                        'is_correct': False
                    }
        return None
    
    def check_common_facts(self, text):
        """Check against common knowledge facts"""
        text_lower = text.lower()
        for fact, truth in self.common_facts.items():
            if fact in text_lower:
                pattern = r'(is|are|equals?|=\s*)(?:\s*not\s*)?\s*(\w+)'
                matches = re.findall(pattern, text_lower)
                for _, claimed_value in matches:
                    if claimed_value != truth:
                        return {
                            'claim': f"{fact} = {claimed_value}",
                            'actual': f"{fact} = {truth}",
                            'is_correct': False
                        }
        return None

    def check_facts(self, text):
        """Main function to check facts in text"""
        # Check date claims first
        date_result = self.check_date_claims(text)
        if date_result:
            return date_result
            
        math_result = self.check_math_claim(text)
        if math_result:
            return math_result
            
        fact_result = self.check_common_facts(text)
        if fact_result:
            return fact_result
            
        return None