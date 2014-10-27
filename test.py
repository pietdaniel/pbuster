q=['1','2','3']

def itra(q):
  o=[]
  for i in q:
    o.append(i+'.txt')
  return o

def gener(q):
  ctr=0
  while ctr<len(q):
      yield q[ctr] + '.txt'
      ctr+=1

print len(gener(q))
r=map(lambda x:x+".q",gener(q))
print(list(r))
f=[i for i in gener(q)]
print(f)
f=itra(q)
print(f)
