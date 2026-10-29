p->prior->next = p->next;
p->next->prior = p->prior;
delete p;
