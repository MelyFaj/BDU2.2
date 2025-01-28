class Fibonacci:
    def __init__(self, n):
        self.n=n

    def generate_sequence(n):
        fibonacci_sequence = []
        a,b=0,1
        for _ in range(n):
            fibonacci_sequence.append(a)
            a,b=b,a+b
        return fibonacci_sequence

        


    def get_nth_term(n):
